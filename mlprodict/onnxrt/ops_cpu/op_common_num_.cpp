
#if !defined(_CRT_SECURE_NO_WARNINGS)
#define _CRT_SECURE_NO_WARNINGS
#endif
#include "op_common_num_.hpp"


#include <xmmintrin.h>
#include <emmintrin.h>


#define BYNF 16


// Optimisation are disabled. The debug version works
// but the release does not.
// It requires further investigation.
#pragma optimize( "", off )
float vector_dot_product_pointer16_sse(const float *p1, const float *p2, size_t size)
{
    float sum = 0;
    size_t i = 0;
    if (size >= BYNF) {
        float r[4];
        size_t size_ = size - size % BYNF;
        __m128 r1 = _mm_setzero_ps();
        for (; i != size_; i += 4, p1 += 4, p2 += 4) {
            r1 = _mm_add_ps(r1, _mm_mul_ps(_mm_load_ps(p1), _mm_load_ps(p2)));
        }
        _mm_store_ps(r, r1);
        sum += r[0] + r[1] + r[2] + r[3];
    }
    size -= i;
    for (; size > 0; ++p1, ++p2, --size)
        sum += *p1 * *p2;
    return sum;
}
#pragma optimize( "", on )


#define BYND 8


#pragma optimize( "", off )
double vector_dot_product_pointer16_sse(const double *p1, const double *p2, size_t size)
{
    double sum = 0;
    size_t i = 0;
    if (size >= BYND) {
        double r[2];
        size_t size_ = size - size % BYND;
        __m128d r1 = _mm_setzero_pd();
        for (; i != size_; i += 2, p1 += 2, p2 += 2) {
            r1 = _mm_add_pd(r1, _mm_mul_pd(_mm_load_pd(p1), _mm_load_pd(p2)));
        }
        _mm_store_pd(r, r1);
        sum += r[0] + r[1];
    }
    size -= i;
    for (; size > 0; ++p1, ++p2, --size)
        sum += *p1 * *p2;
    return sum;
}
#pragma optimize( "", on )


template <>
float vector_dot_product_pointer_sse(const float *p1, const float *p2, size_t size)
{
    return vector_dot_product_pointer16_sse(p1, p2, size);
}

template <>
double vector_dot_product_pointer_sse(const double *p1, const double *p2, size_t size)
{
    return vector_dot_product_pointer16_sse(p1, p2, size);
}

