// Independent physical abc rectifier model. No motulator code is imported.
// Grid -> bridge current is positive; b>0 discharges storage into DC bus.
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using A3=std::array<double,3>;
constexpr double PI=3.1415926535897932384626433832795;
struct Row { double t,p,q,d,u,uc1=0,uc2=0,uc3=0; bool poly=false; };
struct Signal {
 std::vector<Row> a;
 explicit Signal(const std::string& path) {
  std::ifstream f(path); if(!f) throw std::runtime_error("input unavailable");
  std::string s; std::getline(f,s);
  while(std::getline(f,s)) { std::replace(s.begin(),s.end(),',',' '); std::istringstream z(s); Row r; if(z>>r.t>>r.p>>r.q>>r.d>>r.u) {r.poly=bool(z>>r.uc1>>r.uc2>>r.uc3);a.push_back(r);} }
  if(a.size()<2) throw std::runtime_error("two input rows required");
  for(size_t j=1;j<a.size();++j) if(a[j].t<=a[j-1].t) throw std::runtime_error("time must increase");
 }
 std::array<double,6> at(double t) const {
  auto it=std::upper_bound(a.begin(),a.end(),t,[](double x,const Row& r){return x<r.t;});
  size_t k=std::clamp<size_t>(it-a.begin(),1,a.size()-1)-1;
  auto x=a[k],y=a[k+1]; double h=y.t-x.t, v=std::clamp((t-x.t)/h,0.,1.);
  double u=x.poly?x.u+v*(x.uc1+v*(x.uc2+v*x.uc3)):x.u+(y.u-x.u)*v;
  return {x.p+(y.p-x.p)*v,x.q+(y.q-x.q)*v,x.d+(y.d-x.d)*v,u,(y.p-x.p)/h,(y.q-x.q)/h};
 }
};
struct Config {
 double Vrms=690,f=50,L=100e-6,R=.005,C=.02,fs=1e4,dt=1e-6;
 double alpha=2000,tau=.02,umax=5e5,ramp=1e100,W0=19600,B0=1e5,b0=0;
 bool switching=true;
};
struct State { A3 i{}; double W,B,b; };
State add(State a,const State& k,double h) {for(int j=0;j<3;++j)a.i[j]+=h*k.i[j]; a.W+=h*k.W;a.B+=h*k.B;a.b+=h*k.b;return a;}
struct Values {State k; double p,q,loss,load,u,pdc,rawu;};
double dot(A3 a,A3 b) { double z=0; for(int j=0;j<3;++j)z+=a[j]*b[j]; return z; }
A3 phase(double d,double q,double t,double w) {A3 x;for(int j=0;j<3;++j){double th=w*t-2*PI*j/3;x[j]=d*std::cos(th)-q*std::sin(th);}return x;}
std::array<double,2> dq(A3 i,double t,double w) {double d=0,q=0;for(int j=0;j<3;++j){double th=w*t-2*PI*j/3;d+=2./3*i[j]*std::cos(th);q-=2./3*i[j]*std::sin(th);}return {d,q};}
double energyL(const State& y,const Config& c) {return .5*c.L*dot(y.i,y.i);}
Values rhs(double t,const State& y,A3 s,const Signal& sig,const Config& c) {
 if(!(y.W>0)) throw std::runtime_error("nonpositive DC energy");
 auto z=sig.at(t); double V=std::sqrt(2*y.W/c.C),Vp=std::sqrt(2./3)*c.Vrms,w=2*PI*c.f;
 A3 v=phase(Vp,0,t,w),e; double sm=(s[0]+s[1]+s[2])/3;
 Values o; for(int j=0;j<3;++j){e[j]=V*(s[j]-sm);o.k.i[j]=(v[j]-c.R*y.i[j]-e[j])/c.L;}
 auto idq=dq(y.i,t,w);o.p=dot(v,y.i);o.q=1.5*Vp*idq[1];o.pdc=dot(e,y.i);o.loss=c.R*dot(y.i,y.i);o.load=z[2];o.rawu=z[3];o.u=std::clamp(z[3],-c.umax,c.umax);
 o.k.W=o.pdc-o.load+y.b;o.k.B=-y.b;o.k.b=std::clamp((o.u-y.b)/c.tau,-c.ramp,c.ramp);return o;
}
int main(int argc,char**argv) {try {
 if(argc<5) throw std::runtime_error("rectifier input.csv out_prefix avg|pwm dt [fs W0 B0 b0 tau umax ramp]");
 Signal sig(argv[1]);std::string prefix=argv[2];Config c;c.switching=std::string(argv[3])=="pwm";c.dt=std::stod(argv[4]);
 if(argc>5)c.fs=std::stod(argv[5]);
 if(argc>6)c.W0=std::stod(argv[6]);
 if(argc>7)c.B0=std::stod(argv[7]);
 if(argc>8)c.b0=std::stod(argv[8]);
 if(argc>9)c.tau=std::stod(argv[9]);
 if(argc>10)c.umax=std::stod(argv[10]);
 if(argc>11)c.ramp=std::stod(argv[11]);
 if(argc>12)c.L=std::stod(argv[12]);
 if(argc>13)c.R=std::stod(argv[13]);
 if(argc>14)c.C=std::stod(argv[14]);
 if(argc>15)c.Vrms=std::stod(argv[15]);
 if(argc>16)c.alpha=std::stod(argv[16]);
 double Vp=std::sqrt(2./3)*c.Vrms,w=2*PI*c.f,Ts=1/c.fs,tend=sig.a.back().t;
 auto z0=sig.at(0);State y{phase(z0[0]/(1.5*Vp),z0[1]/(1.5*Vp),0,w),c.W0,c.B0,c.b0};
 double E0=y.W+y.B+energyL(y,c),acint=0,lossint=0,loadint=0,batint=0,bridgeint=0,closuremax=0;
 double integ_d=0,integ_q=0,peakI=0,minV=std::sqrt(2*y.W/c.C),maxV=minV,maxM=0,maxCircularM=0,maxRawU=0,maxBdot=0,maxUclip=0,maxRateclip=0;long nsteps=0,nclip=0;
 std::ofstream out(prefix+".csv"),raw(prefix+"_waveform.csv");out<<std::setprecision(14);raw<<std::setprecision(14);
 out<<"t,W,B,b,id,iq,ia,ib,ic,Pmean,Qmean,Pcmd,Qcmd,dmean,umean,Pdcmean,lossmean,Vmin,Vmax,Imax,modulation,clipped,energy_closure,grid_energy,loss_energy,load_energy,battery_energy,bridge_energy,filter_energy,circular_modulation\n";
 raw<<"t,ia,ib,ic,Vdc,b,W,B,sa,sb,sc,ea,eb,ec,P,Q,pdc\n";
 for(long cycle=0;cycle*Ts<tend-1e-13;++cycle) {
  double t0=cycle*Ts,t1=std::min(t0+Ts,tend),period=t1-t0;auto z=sig.at(t0),zf=sig.at(t0+.5*period);auto im=dq(y.i,t0,w);
  double id=z[0]/(1.5*Vp),iq=z[1]/(1.5*Vp),idf=zf[0]/(1.5*Vp),iqf=zf[1]/(1.5*Vp);
  double errd=im[0]-id,errq=im[1]-iq;
  double ed=Vp-c.R*idf+w*c.L*iqf-c.L*zf[4]/(1.5*Vp)+c.L*c.alpha*errd+c.R*c.alpha*integ_d;
  double eq=-c.R*iqf-w*c.L*idf-c.L*zf[5]/(1.5*Vp)+c.L*c.alpha*errq+c.R*c.alpha*integ_q;
  A3 e=phase(ed,eq,t0+.5*period,w),duty;double vdc=std::sqrt(2*y.W/c.C),emin=*std::min_element(e.begin(),e.end()),emax=*std::max_element(e.begin(),e.end()),zero=(emin+emax)/2,mod=(emax-emin)/vdc;
  double circular_mod=std::sqrt(3.)*std::hypot(ed,eq)/vdc;
  bool clip=mod>1;maxM=std::max(maxM,mod);maxCircularM=std::max(maxCircularM,circular_mod);if(clip)++nclip;else{integ_d+=period*errd;integ_q+=period*errq;}
  std::vector<double> edges={t0,t1};for(int j=0;j<3;++j){duty[j]=std::clamp(.5+(e[j]-zero)/vdc,0.,1.);if(c.switching){edges.push_back(t0+.5*period*(1-duty[j]));edges.push_back(t0+.5*period*(1+duty[j]));}}
  auto knot=std::upper_bound(sig.a.begin(),sig.a.end(),t0+1e-13,[](double x,const Row& r){return x<r.t;});
  for(;knot!=sig.a.end()&&knot->t<t1-1e-13;++knot)edges.push_back(knot->t);
  std::sort(edges.begin(),edges.end());edges.erase(std::unique(edges.begin(),edges.end(),[](double a,double b){return std::abs(a-b)<1e-14;}),edges.end());
  double pm=0,qm=0,lm=0,dm=0,um=0,pcm=0,cycleminV=vdc,cyclemaxV=vdc,cyclemaxI=0;
  for(size_t edge=0;edge+1<edges.size();++edge){double ta=edges[edge],tb=edges[edge+1];if(tb-ta<1e-14)continue;A3 sw=duty;
   if(c.switching){double carrier=std::abs(2*((ta+tb)/2-t0)/period-1);for(int j=0;j<3;++j)sw[j]=duty[j]>carrier?1:0;}
   int ns=std::max(1,(int)std::ceil((tb-ta)/c.dt));double h=(tb-ta)/ns;
   for(int k=0;k<ns;++k){double t=ta+k*h;auto a=rhs(t,y,sw,sig,c);State ym=add(y,a.k,h/2);auto b=rhs(t+h/2,ym,sw,sig,c);y=add(y,b.k,h);++nsteps;
    pm+=h*b.p;qm+=h*b.q;lm+=h*b.loss;dm+=h*b.load;um+=h*b.u;pcm+=h*b.pdc;acint+=h*b.p;lossint+=h*b.loss;loadint+=h*b.load;batint+=h*ym.b;bridgeint+=h*b.pdc;
    maxRawU=std::max(maxRawU,std::abs(b.rawu));maxBdot=std::max(maxBdot,std::abs(b.k.b));maxUclip=std::max(maxUclip,std::abs(b.u-b.rawu));maxRateclip=std::max(maxRateclip,std::abs((b.u-ym.b)/c.tau-b.k.b));
    double vv=std::sqrt(2*y.W/c.C),ii=std::sqrt(2./3*dot(y.i,y.i));cycleminV=std::min(cycleminV,vv);cyclemaxV=std::max(cyclemaxV,vv);cyclemaxI=std::max(cyclemaxI,ii);closuremax=std::max(closuremax,std::abs(y.W+y.B+energyL(y,c)-E0-acint+lossint+loadint));
    if(t+h/2>=tend-.002){double vm=std::sqrt(2*ym.W/c.C),sm=(sw[0]+sw[1]+sw[2])/3;raw<<t+h/2;for(auto x:ym.i)raw<<','<<x;raw<<','<<vm<<','<<ym.b<<','<<ym.W<<','<<ym.B;for(auto x:sw)raw<<','<<x;for(auto x:sw)raw<<','<<vm*(x-sm);raw<<','<<b.p<<','<<b.q<<','<<b.pdc<<'\n';}
   }
  }
  minV=std::min(minV,cycleminV);maxV=std::max(maxV,cyclemaxV);peakI=std::max(peakI,cyclemaxI);auto iy=dq(y.i,t1,w);auto zm=sig.at((t0+t1)/2);double closure=y.W+y.B+energyL(y,c)-E0-acint+lossint+loadint;
  out<<t1<<','<<y.W<<','<<y.B<<','<<y.b<<','<<iy[0]<<','<<iy[1];for(auto x:y.i)out<<','<<x;
  out<<','<<pm/period<<','<<qm/period<<','<<zm[0]<<','<<zm[1]<<','<<dm/period<<','<<um/period<<','<<pcm/period<<','<<lm/period<<','<<cycleminV<<','<<cyclemaxV<<','<<cyclemaxI<<','<<mod<<','<<clip<<','<<closure<<','<<acint<<','<<lossint<<','<<loadint<<','<<batint<<','<<bridgeint<<','<<energyL(y,c)<<','<<circular_mod<<'\n';
 }
 std::cout<<std::setprecision(12)<<"{\"steps\":"<<nsteps<<",\"Vmin\":"<<minV<<",\"Vmax\":"<<maxV<<",\"Ipeak\":"<<peakI<<",\"modulation_max\":"<<maxM<<",\"circular_modulation_max\":"<<maxCircularM<<",\"clipped_cycles\":"<<nclip<<",\"energy_closure_max_J\":"<<closuremax<<",\"Wfinal\":"<<y.W<<",\"Bfinal\":"<<y.B<<",\"bfinal\":"<<y.b<<",\"requested_u_peak_W\":"<<maxRawU<<",\"actual_bdot_peak_W_per_s\":"<<maxBdot<<",\"u_clamp_max_change_W\":"<<maxUclip<<",\"rate_clamp_max_change_W_per_s\":"<<maxRateclip<<"}\n";
 }catch(const std::exception& ex){std::cerr<<ex.what()<<'\n';return 1;}return 0;}
