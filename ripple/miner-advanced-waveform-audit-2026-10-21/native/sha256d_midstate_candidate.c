/* Independent candidate: Bitcoin SHA-256d with 64-byte midstate reuse.
 * Original Ripple miner C backend remains unchanged.
 * OpenSSL's SHA256 incremental interface produces exact SHA256 bytes.
 * This file is a measured optimization candidate, not a rewritten hash.
 */
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>

static int le256_below(const uint8_t *digest, const uint8_t *limit) {
    for (int i=31;i>=0;i--) {
        if (digest[i] < limit[i]) return 1;
        if (digest[i] > limit[i]) return 0;
    }
    return 1;
}

/* Match the exact existing ctypes ABI to enable drop-in ablation. */
int64_t ripple_scan_sha256d(const uint8_t *prefix, uint32_t start, uint32_t count,
        const uint8_t *share_target, const uint8_t *block_target,
        uint32_t *out_nonces, uint8_t *out_digests, uint8_t *out_blocks,
        uint32_t max_matches) {
    if (!prefix || !share_target || !block_target || !out_nonces || !out_digests || !out_blocks ||
        (uint64_t)start+(uint64_t)count > 4294967296ULL) return -2;
    uint8_t tail[16],first[32],digest[32];
    SHA256_CTX base, context;
    if (SHA256_Init(&base)!=1 || SHA256_Update(&base,prefix,64)!=1) return -3;
    memcpy(tail,prefix+64,12);
    uint32_t matches=0;
    for (uint32_t i=0;i<count;i++) {
        const uint32_t nonce=start+i;
        tail[12]=(uint8_t)(nonce);tail[13]=(uint8_t)(nonce>>8);
        tail[14]=(uint8_t)(nonce>>16);tail[15]=(uint8_t)(nonce>>24);
        memcpy(&context,&base,sizeof(base));
        if (SHA256_Update(&context,tail,16)!=1 || SHA256_Final(first,&context)!=1) return -3;
        SHA256(first,32,digest);
        if(le256_below(digest,share_target)) {
            if(matches>=max_matches)return -1;
            out_nonces[matches]=nonce;
            memcpy(out_digests+32*matches,digest,32);
            out_blocks[matches]=(uint8_t)le256_below(digest,block_target);
            matches++;
        }
    }
    return (int64_t)matches;
}