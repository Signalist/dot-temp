// V2 causal total stored-energy recovery: copied physical equations and current loop from original_rectifier.cpp.
// Healthy comparison is not an input to this executable. Plant tau/ramp never enter control.
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
constexpr double VP=563.3826408401309,OM=2*PI*50,L=.0003,R=.005,C=.03,TS=.0001;
constexpr double PBASE=654498.72485653043,WSET=21600,BSET=50000,T=0.2,WARM=2.0;
struct Row { double t,p,q,d,u,uc1=0,uc2=0,uc3=0; bool poly=false; };
struct Signal {
 std::vector<Row> a;
 explicit Signal(const std::string& path) {
  std::ifstream f(path);if(!f)throw std::runtime_error("input unavailable");std::string s;std::getline(f,s);
  while(std::getline(f,s)){std::replace(s.begin(),s.end(),',',' ');std::istringstream z(s);Row r;if(z>>r.t>>r.p>>r.q>>r.d>>r.u){r.poly=bool(z>>r.uc1>>r.uc2>>r.uc3);a.push_back(r);}}
  if(a.size()<2)throw std::runtime_error("two input rows required");
 }
 std::array<double,6> at(double t) const {
  auto it=std::upper_bound(a.begin(),a.end(),t,[](double x,const Row&r){return x<r.t;});size_t k=std::clamp<size_t>(it-a.begin(),1,a.size()-1)-1;
  auto x=a[k],y=a[k+1];double h=y.t-x.t,v=std::clamp((t-x.t)/h,0.,1.);double u=x.poly?x.u+v*(x.uc1+v*(x.uc2+v*x.uc3)):x.u+(y.u-x.u)*v;
  return{x.p+(y.p-x.p)*v,x.q+(y.q-x.q)*v,x.d+(y.d-x.d)*v,u,(y.p-x.p)/h,(y.q-x.q)/h};
 }
};
struct State { A3 i{};double W=WSET,B=BSET,b=0;};
struct Control { double jd=0,jq=0,zw=0,cp=0,held=0,ub=0;bool frozen=false;A3 duty{};double mod=0,circular=0;long clip=0;};
struct Integral {double ac=0,loss=0,load=0,bat=0,bridge=0;};
struct Config {double dt=1e-6,tau=.005,ramp=30e6,onset=2,tend=2.9;bool warm=false,service=true;};
struct Extrema {double Vmin=1e100,Vmax=-1e100,Iphase=0,Ispace=0,Bmin=1e100,Bmax=-1e100,bpeak=0,rawu=0,u=0,bdot=0,uclip=0,rateclip=0,mod=0,circular=0,closure=0,Pmin=1e100,Pmax=-1e100,Qmin=1e100,Qmax=-1e100;};
double dot(A3 a,A3 b){double z=0;for(int j=0;j<3;++j)z+=a[j]*b[j];return z;}
A3 phase(double d,double q,double t){A3 x;for(int j=0;j<3;++j){double th=OM*t-2*PI*j/3;x[j]=d*std::cos(th)-q*std::sin(th);}return x;}
std::array<double,2> dq(A3 i,double t){double d=0,q=0;for(int j=0;j<3;++j){double th=OM*t-2*PI*j/3;d+=2./3*i[j]*std::cos(th);q-=2./3*i[j]*std::sin(th);}return{d,q};}
State add(State a,const State&k,double h){for(int j=0;j<3;++j)a.i[j]+=h*k.i[j];a.W+=h*k.W;a.B+=h*k.B;a.b+=h*k.b;return a;}
double EL(const State&y){return .5*L*dot(y.i,y.i);}
std::array<double,6> command(double t,const Signal&sig,const Config&c){if(c.warm||!c.service||t<c.onset||t>=c.onset+T)return{PBASE,0,650000,0,0,0};return sig.at(t-c.onset);}
struct Values{State k;double p,q,loss,load,u,pdc,rawu,pcmd,qcmd,rawrate;};
Values rhs(double t,const State&y,A3 sw,const Signal&sig,const Config&c,const Control&ctrl){
 if(!(y.W>0))throw std::runtime_error("nonpositive DC energy");auto z=command(t,sig,c);double V=std::sqrt(2*y.W/C);A3 v=phase(VP,0,t),e;double sm=(sw[0]+sw[1]+sw[2])/3;Values o;
 for(int j=0;j<3;++j){e[j]=V*(sw[j]-sm);o.k.i[j]=(v[j]-R*y.i[j]-e[j])/L;}
 auto iq=dq(y.i,t);o.p=dot(v,y.i);o.q=1.5*VP*iq[1];o.pdc=dot(e,y.i);o.loss=R*dot(y.i,y.i);o.load=z[2];o.pcmd=z[0];o.qcmd=z[1];o.rawu=z[3]+ctrl.ub;o.u=std::clamp(o.rawu,-450000.,450000.);
 o.k.W=o.pdc-o.load+y.b;o.k.B=-y.b;o.rawrate=(o.u-y.b)/c.tau;o.k.b=std::clamp(o.rawrate,-c.ramp,c.ramp);return o;
}
void snapshot(std::ostream&o,double t,const State&y,const Control&a,const Integral&z){o<<std::setprecision(17)<<t;for(double x:y.i)o<<','<<x;o<<','<<y.W<<','<<y.B<<','<<y.b<<','<<a.jd<<','<<a.jq<<','<<a.zw<<','<<a.cp<<','<<a.held<<','<<a.ub<<','<<a.frozen;for(double x:a.duty)o<<','<<x;o<<','<<z.ac<<','<<z.loss<<','<<z.load<<','<<z.bat<<','<<z.bridge<<','<<EL(y)<<'\n';}
const char* snapheader="t,ia,ib,ic,W,B,b,jd,jq,zw,cp,held,ub,frozen,da,db,dc,grid_energy,loss_energy,load_energy,battery_energy,bridge_energy,filter_energy\n";
void savecheckpoint(const std::string&path,const State&y,const Control&a){std::ofstream o(path);o<<snapheader;snapshot(o,2,y,a,Integral{});}
void loadcheckpoint(const std::string&path,State&y,Control&a){std::ifstream f(path);std::string s;std::getline(f,s);std::getline(f,s);std::replace(s.begin(),s.end(),',',' ');std::istringstream z(s);double t;z>>t;for(auto&x:y.i)z>>x;z>>y.W>>y.B>>y.b>>a.jd>>a.jq>>a.zw>>a.cp>>a.held>>a.ub>>a.frozen;for(auto&x:a.duty)z>>x;if(!z||t!=2)throw std::runtime_error("bad checkpoint");}
void extrema(Extrema&x,const State&y,const Values&o,const Config&c){double v=std::sqrt(2*y.W/C);x.Vmin=std::min(x.Vmin,v);x.Vmax=std::max(x.Vmax,v);for(double i:y.i)x.Iphase=std::max(x.Iphase,std::abs(i));x.Ispace=std::max(x.Ispace,std::sqrt(2./3*dot(y.i,y.i)));x.Bmin=std::min(x.Bmin,y.B);x.Bmax=std::max(x.Bmax,y.B);x.bpeak=std::max(x.bpeak,std::abs(y.b));x.rawu=std::max(x.rawu,std::abs(o.rawu));x.u=std::max(x.u,std::abs(o.u));x.bdot=std::max(x.bdot,std::abs(o.k.b));x.uclip=std::max(x.uclip,std::abs(o.rawu-o.u));x.rateclip=std::max(x.rateclip,std::abs(o.rawrate-o.k.b));x.Pmin=std::min(x.Pmin,o.p);x.Pmax=std::max(x.Pmax,o.p);x.Qmin=std::min(x.Qmin,o.q);x.Qmax=std::max(x.Qmax,o.q);(void)c;}
int main(int argc,char**argv){try{
 if(argc<6)throw std::runtime_error("recovery warmup|case input.csv prefix dt checkpoint [tau ramp onset_offset service]");std::string mode=argv[1],prefix=argv[3],cpfile=argv[5];Signal sig(argv[2]);Config c;c.dt=std::stod(argv[4]);c.warm=mode=="warmup";State y;Control ctrl;
 if(c.warm){y.i=phase(PBASE/(1.5*VP),0,0);c.tend=2;}else{if(argc<10)throw std::runtime_error("case args missing");c.tau=std::stod(argv[6]);c.ramp=std::stod(argv[7]);c.onset=2+std::stod(argv[8]);c.service=std::stoi(argv[9]);c.tend=c.onset+T+.7;loadcheckpoint(cpfile,y,ctrl);}
 double start=c.warm?0:2,E0=y.W+y.B+EL(y);Integral ints;Extrema all,svc,rec;std::ofstream out(prefix+".csv"),dense(prefix+"_dense.csv"),snaps(prefix+"_snapshots.csv"),bins(prefix+"_bins.csv");out<<std::setprecision(17);dense<<std::setprecision(17);snaps<<snapheader;dense<<snapheader;
 out<<"t,W,B,b,ia,ib,ic,jd,jq,zw,cp,held,ub,da,db,dc,Pmean,Qmean,Pcmdmean,Qcmdmean,loadmean,umean,lossmean,pdcmean,grid_energy,loss_energy,load_energy,battery_energy,bridge_energy,filter_energy,closure,mod,circular\n";
 snapshot(snaps,start,y,ctrl,ints);double binp[10]={},binq[10]={},bincp[10]={},bincq[10]={},bind[10]={};
 std::vector<double> milestones;if(!c.warm)milestones={c.onset,c.onset+T,c.onset+T+.5,c.tend};size_t milestone=0;
 while(milestone<milestones.size()&&std::abs(milestones[milestone]-start)<1e-12){snapshot(snaps,start,y,ctrl,ints);++milestone;}
 long first=std::llround(start/TS),last=std::ceil(c.tend/TS-1e-9);long steps=0;
 for(long cycle=first;cycle<last;++cycle){double t0=cycle*TS,t1=std::min(t0+TS,c.tend),period=t1-t0;if(period<=1e-14)continue;
  bool gate=!c.warm&&(t0+TS>c.onset+1e-12)&&(t0<c.onset+T-1e-12);double eW=WSET+BSET-y.W-y.B;
  if(gate){if(!ctrl.frozen){ctrl.held=ctrl.cp;ctrl.frozen=true;}ctrl.cp=ctrl.held;ctrl.ub=0;}
  else{ctrl.frozen=false;double raw=100*eW+2500*ctrl.zw;ctrl.cp=std::clamp(raw,-4500.,4500.);if(!(raw>=4500&&eW>0)&&!(raw<=-4500&&eW<0))ctrl.zw+=TS*eW;ctrl.ub=std::clamp(20*(y.B-BSET),-10000.,10000.);}
  auto z=command(t0,sig,c),zf=command(t0+.5*TS,sig,c);auto im=dq(y.i,t0);double id=(z[0]+ctrl.cp)/(1.5*VP),iq=z[1]/(1.5*VP),idf=(zf[0]+ctrl.cp)/(1.5*VP),iqf=zf[1]/(1.5*VP);double errd=im[0]-id,errq=im[1]-iq;
  double ed=VP-R*idf+OM*L*iqf-L*zf[4]/(1.5*VP)+L*2000*errd+R*2000*ctrl.jd;
  double eq=-R*iqf-OM*L*idf-L*zf[5]/(1.5*VP)+L*2000*errq+R*2000*ctrl.jq;
  A3 e=phase(ed,eq,t0+.5*TS);double vdc=std::sqrt(2*y.W/C),emin=*std::min_element(e.begin(),e.end()),emax=*std::max_element(e.begin(),e.end()),zero=(emin+emax)/2;
  ctrl.mod=(emax-emin)/vdc;ctrl.circular=std::sqrt(3.)*std::hypot(ed,eq)/vdc;if(ctrl.mod>1)++ctrl.clip;else{ctrl.jd+=TS*errd;ctrl.jq+=TS*errq;}
  std::vector<double> edges={t0,t1};for(int j=0;j<3;++j){ctrl.duty[j]=std::clamp(.5+(e[j]-zero)/vdc,0.,1.);double lo=t0+.5*TS*(1-ctrl.duty[j]),hi=t0+.5*TS*(1+ctrl.duty[j]);if(lo<t1)edges.push_back(lo);if(hi<t1)edges.push_back(hi);}
  if(!c.warm){for(auto r:sig.a){double kt=c.onset+r.t;if(kt>t0+1e-13&&kt<t1-1e-13)edges.push_back(kt);}for(double mt:milestones)if(mt>t0+1e-13&&mt<t1-1e-13)edges.push_back(mt);for(int n=0;n<=10;++n){double bt=c.onset+n*.02;if(bt>t0+1e-13&&bt<t1-1e-13)edges.push_back(bt);}}
  // Fixed absolute 1 us sampling grid in final 100 ms before deadline. It only refines integration events.
  double dense_lo=c.onset+T+.4,dense_hi=c.onset+T+.5;
  if(!c.warm&&t1>=dense_lo-1e-12&&t0<=dense_hi+1e-12){long lo=std::ceil((std::max(t0,dense_lo)-1e-12)/1e-6),hi=std::floor((std::min(t1,dense_hi)+1e-12)/1e-6);for(long n=lo;n<=hi;++n){double tt=n*1e-6;if(tt>t0+1e-13&&tt<t1-1e-13)edges.push_back(tt);}}
  std::sort(edges.begin(),edges.end());edges.erase(std::unique(edges.begin(),edges.end(),[](double a,double b){return std::abs(a-b)<1e-13;}),edges.end());
  double pm=0,qm=0,pcm=0,qcm=0,lm=0,dm=0,um=0,pdcm=0;
  for(size_t edge=0;edge+1<edges.size();++edge){double ta=edges[edge],tb=edges[edge+1];if(tb-ta<1e-14)continue;double carrier=std::abs(2*((ta+tb)/2-t0)/TS-1);A3 sw;for(int j=0;j<3;++j)sw[j]=ctrl.duty[j]>carrier?1:0;
   int ns=std::max(1,(int)std::ceil((tb-ta)/c.dt));double h=(tb-ta)/ns;
   for(int k=0;k<ns;++k){double tt=ta+k*h;auto a=rhs(tt,y,sw,sig,c,ctrl);State ym=add(y,a.k,h/2);auto b=rhs(tt+h/2,ym,sw,sig,c,ctrl);y=add(y,b.k,h);++steps;
    pm+=h*b.p;qm+=h*b.q;pcm+=h*b.pcmd;qcm+=h*b.qcmd;lm+=h*b.loss;dm+=h*b.load;um+=h*b.u;pdcm+=h*b.pdc;ints.ac+=h*b.p;ints.loss+=h*b.loss;ints.load+=h*b.load;ints.bat+=h*ym.b;ints.bridge+=h*b.pdc;
    extrema(all,y,b,c);extrema(all,ym,b,c);all.mod=std::max(all.mod,ctrl.mod);all.circular=std::max(all.circular,ctrl.circular);all.closure=std::max(all.closure,std::abs(y.W+y.B+EL(y)-E0-ints.ac+ints.loss+ints.load));
    if(tt+h/2>=c.onset&&tt+h/2<c.onset+T){extrema(svc,y,b,c);extrema(svc,ym,b,c);svc.mod=std::max(svc.mod,ctrl.mod);svc.circular=std::max(svc.circular,ctrl.circular);int j=std::clamp(int((tt+h/2-c.onset)/.02),0,9);binp[j]+=h*b.p;binq[j]+=h*b.q;bincp[j]+=h*b.pcmd;bincq[j]+=h*b.qcmd;bind[j]+=h;}
    if(tt+h/2>=c.onset+T){extrema(rec,y,b,c);extrema(rec,ym,b,c);rec.mod=std::max(rec.mod,ctrl.mod);rec.circular=std::max(rec.circular,ctrl.circular);}
   }
   if(!c.warm&&tb>=dense_lo-1e-12&&tb<=dense_hi+1e-12&&std::abs(tb/1e-6-std::round(tb/1e-6))<1e-6)snapshot(dense,tb,y,ctrl,ints);
   while(milestone<milestones.size()&&std::abs(tb-milestones[milestone])<1e-11){snapshot(snaps,tb,y,ctrl,ints);++milestone;}
  }
  if(!c.warm||t1>=1.86-1e-12){out<<t1<<','<<y.W<<','<<y.B<<','<<y.b;for(double a:y.i)out<<','<<a;out<<','<<ctrl.jd<<','<<ctrl.jq<<','<<ctrl.zw<<','<<ctrl.cp<<','<<ctrl.held<<','<<ctrl.ub;for(double a:ctrl.duty)out<<','<<a;out<<','<<pm/period<<','<<qm/period<<','<<pcm/period<<','<<qcm/period<<','<<dm/period<<','<<um/period<<','<<lm/period<<','<<pdcm/period<<','<<ints.ac<<','<<ints.loss<<','<<ints.load<<','<<ints.bat<<','<<ints.bridge<<','<<EL(y)<<','<<y.W+y.B+EL(y)-E0-ints.ac+ints.loss+ints.load<<','<<ctrl.mod<<','<<ctrl.circular<<'\n';}
 }
 if(c.warm){savecheckpoint(cpfile,y,ctrl);snapshot(snaps,2,y,ctrl,ints);}bins<<"cycle,duration,Pmean,Qmean,Pcmdmean,Qcmdmean\n";bins<<std::setprecision(17);for(int j=0;j<10;++j)if(bind[j]>0)bins<<j<<','<<bind[j]<<','<<binp[j]/bind[j]<<','<<binq[j]/bind[j]<<','<<bincp[j]/bind[j]<<','<<bincq[j]/bind[j]<<'\n';
 auto jext=[](const Extrema&x){std::ostringstream o;o<<std::setprecision(17)<<"{\"Vmin\":"<<x.Vmin<<",\"Vmax\":"<<x.Vmax<<",\"Iphase\":"<<x.Iphase<<",\"Ispace\":"<<x.Ispace<<",\"Bmin\":"<<x.Bmin<<",\"Bmax\":"<<x.Bmax<<",\"bpeak\":"<<x.bpeak<<",\"rawu\":"<<x.rawu<<",\"u\":"<<x.u<<",\"bdot\":"<<x.bdot<<",\"uclip\":"<<x.uclip<<",\"rateclip\":"<<x.rateclip<<",\"mod\":"<<x.mod<<",\"circular\":"<<x.circular<<",\"closure\":"<<x.closure<<",\"Pmin\":"<<x.Pmin<<",\"Pmax\":"<<x.Pmax<<",\"Qmin\":"<<x.Qmin<<",\"Qmax\":"<<x.Qmax<<"}";return o.str();};
 std::cout<<"{\"steps\":"<<steps<<",\"clipped_cycles\":"<<ctrl.clip<<",\"all\":"<<jext(all)<<",\"service\":"<<jext(svc)<<",\"recovery\":"<<jext(rec)<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}return 0;}
