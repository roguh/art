#define S 3321
main(i,x,y,t){float r,m,R[S]={0},M[S]={0},C[S],D[S];for(i=0;i<S;i++){C[i]=2.5*(i%81)/80.-2;D[i]=2*(i/81)/40.-1;}t=0;while(t++<1063){for(i=0;i<S;i++){r=R[i];m=M[i];R[i]=r*r-m*m+C[i];M[i]=2*r*m+D[i];}}for(i=0;i<S;i++){printf(R[i]*R[i]+M[i]*M[i]<4?"█":"▒");i%81==80&&puts("");}}
