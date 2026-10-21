/* Native CPU SHA-256d batch scanner. OpenSSL SHA256 is used for both rounds.
 * The returned bytes are the real digest; the Python caller independently
 * verifies every candidate nonce before submission to a mining pool.
 * No SIMD, GPU, ASIC or fabricated acceleration claims.
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
/* Results: -1 if no buffer space, -2 for bad arguments; otherwise count.
 * On -1 caller must rerun with a larger buffer or Python scan.
 */
int64_t ripple_scan_sha256d(const uint8_t *prefix, uint32_t start, uint32_t count,
        const uint8_t *share_target, const uint8_t *block_target,
        uint32_t *out_nonces, uint8_t *out_digests, uint8_t *out_blocks,
        uint32_t max_matches) {
    if (!prefix || !share_target || !block_target || !out_nonces || !out_digests || !out_blocks ||
        (uint64_t)start+(uint64_t)count > 4294967296ULL) return -2;
    uint8_t header[80],first[32],digest[32];
    memcpy(header,prefix,76);
    uint32_t matches=0;
    for(uint32_t i=0;i<count;i++) {
        uint32_t nonce=start+i;
        header[76]=nonce & 255; header[77]=(nonce>>8)&255;
        header[78]=(nonce>>16)&255;header[79]=(nonce>>24)&255;
        SHA256(header,80,first);SHA256(first,32,digest);
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