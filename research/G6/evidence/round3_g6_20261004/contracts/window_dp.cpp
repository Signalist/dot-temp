#include <algorithm>
#include <array>
#include <cmath>
#include <vector>
// Exact max-plus dynamic program in ordinary double arithmetic. Inputs are
// reward advantages r1-r0; adding the common-sign sum r0 occurs in Python.
extern "C" void window_dp(const double* d, int rows, int n, int L, int B, double* out) {
  int S=1<<(L-1), half=S/2;
  std::vector<int> masks, p0, p1;
  std::vector<int> index(S,-1);
  for(int s=0;s<S;++s) if(__builtin_popcount((unsigned)s)<=B) {index[s]=masks.size(); masks.push_back(s);}
  int K=masks.size();
  for(int s:masks) {
    int a=s>>1,b=a|half,bit=s&1;
    p0.push_back(__builtin_popcount((unsigned)a)+bit<=B ? index[a]:-1);
    p1.push_back(__builtin_popcount((unsigned)b)+bit<=B ? index[b]:-1);
  }
  #pragma omp parallel for schedule(static)
  for(int row=0;row<rows;++row) {
    std::array<double,128> x,y;
    x.fill(-INFINITY);x[index[0]]=0.;
    for(int t=0;t<n;++t) {
      const double gain=d[(long long)row*n+t];
      for(int k=0;k<K;++k) {
        double v=-INFINITY;
        if(p0[k]>=0)v=x[p0[k]];
        if(p1[k]>=0)v=std::max(v,x[p1[k]]);
        y[k]=v+((masks[k]&1)?gain:0.);
      }
      std::copy(y.begin(),y.begin()+K,x.begin());
    }
    out[row]=*std::max_element(x.begin(),x.begin()+K);
  }
}
