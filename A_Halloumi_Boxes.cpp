#include <iostream>
#include <algorithm>
using namespace std;


int main(){
    int t;
    cin>>t;
    while(t--){
        int n,k;
        cin>>n;
        cin>>k;
        int arr[n];
        for(int i=0;i<n;i++){
            cin>>arr[i];
        }
        bool sorted =true;
        if(k>=2){
            cout<<"YES"<<"\n";
        }
        else{
            for(int i=0;i<n-1;i++){
                if(arr[i]>arr[i+1]) {sorted = false;
                break;}
            }
            sorted ? cout<<"YES\n": cout<<"NO\n"; 
        }
    }
}