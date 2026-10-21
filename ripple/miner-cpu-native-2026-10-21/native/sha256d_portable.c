/* Portable exact Bitcoin SHA256d nonce scanner. Standalone SHA-256 compression
 * with the 64-byte header midstate reused; no external libraries required.
 * Verify with Python's hashlib and Bitcoin genesis before using in production.
 */
#include <stdint.h>
#include <string.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
#define CH(x,y,z) (((x)&(y))^(~(x)&(z)))
#define MAJ(x,y,z) (((x)&(y))^((x)&(z))^((y)&(z)))
#define S0(x) (ROR(x,2)^ROR(x,13)^ROR(x,22))
#define S1(x) (ROR(x,6)^ROR(x,11)^ROR(x,25))
#define s0(x) (ROR(x,7)^ROR(x,18)^((x)>>3))
#define s1(x) (ROR(x,17)^ROR(x,19)^((x)>>10))
static const uint32_t K[64]={
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static const uint32_t IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static uint32_t load_be(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
static void store_be(uint8_t *p,uint32_t v){p[0]=v>>24;p[1]=v>>16;p[2]=v>>8;p[3]=v;}
static void transform(uint32_t H[8], const uint8_t block[64]){
    uint32_t w[64];
    for(int i=0;i<16;i++)w[i]=load_be(block+4*i);
    for(int i=16;i<64;i++)w[i]=s1(w[i-2])+w[i-7]+s0(w[i-15])+w[i-16];
    uint32_t a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
    for(int i=0;i<64;i++){
        uint32_t t1=h+S1(e)+CH(e,f,g)+K[i]+w[i],t2=S0(a)+MAJ(a,b,c);
        h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;
    }
    H[0]+=a;H[1]+=b;H[2]+=c;H[3]+=d;H[4]+=e;H[5]+=f;H[6]+=g;H[7]+=h;
}
static int under(const uint8_t *digest,const uint8_t *limit){
    /* The SHA digest is a 32-byte big-endian SHA output. Bitcoin compares it
     * as a little-endian integer, so high-significance bytes are at the end. */
    for(int i=31;i>=0;i--){if(digest[i]<limit[i])return 1;if(digest[i]>limit[i])return 0;}return 1;
}
API int64_t ripple_scan_sha256d(const uint8_t *prefix,uint32_t start,uint32_t count,
     const uint8_t *share_target,const uint8_t *block_target,
     uint32_t *out_nonces,uint8_t *out_digests,uint8_t *out_blocks,uint32_t max_matches){
    if(!prefix||!share_target||!block_target||!out_nonces||!out_digests||!out_blocks||
       (uint64_t)start+(uint64_t)count>UINT64_C(4294967296))return -2;
    uint32_t base[8];memcpy(base,IV,sizeof(base));transform(base,prefix);
    uint8_t block1[64]={0},block2[64]={0},digest[32];
    memcpy(block1,prefix+64,12);
    block1[16]=0x80;block1[62]=0x02;block1[63]=0x80; /* original 80-byte header is 640 bits */
    block2[32]=0x80;block2[62]=0x01;block2[63]=0x00; /* inner digest 32 bytes is 256 bits */
    uint32_t matches=0;
    for(uint32_t i=0;i<count;i++){
       uint32_t nonce=start+i;
       block1[12]=(uint8_t)nonce;block1[13]=(uint8_t)(nonce>>8);
       block1[14]=(uint8_t)(nonce>>16);block1[15]=(uint8_t)(nonce>>24);
       uint32_t state[8];memcpy(state,base,sizeof(base));transform(state,block1);
       for(int j=0;j<8;j++)store_be(block2+j*4,state[j]);
       memcpy(state,IV,sizeof(state));transform(state,block2);
       for(int j=0;j<8;j++)store_be(digest+j*4,state[j]);
       if(under(digest,share_target)){
           if(matches>=max_matches)return -1;
           out_nonces[matches]=nonce;memcpy(out_digests+32*matches,digest,32);
           out_blocks[matches]=(uint8_t)under(digest,block_target);
           matches++;
       }
    }
    return (int64_t)matches;
}