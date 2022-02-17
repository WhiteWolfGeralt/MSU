#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <omp.h>
#include <sys/time.h>
#define  Max(a,b) ((a)>(b)?(a):(b))

#define MEDIUM_DATASET

# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(MEDIUM_DATASET) && !defined(LARGE_DATASET) && !defined(CHECK_DATASET)
#define LARGE_DATASET
# endif

# ifdef CHECK_DATASET
#define  N 10
# endif

# ifdef MINI_DATASET
#define  N 34
# endif

# ifdef SMALL_DATASET
#define  N 130
# endif

# ifdef MEDIUM_DATASET
#define  N 258
# endif

# ifdef LARGE_DATASET
#define  N 514
# endif

float maxeps = 0.1e-7;
int itmax = 100;
int i, j, k;
float w = 0.5;
float eps;
float b;
struct timeval start_time, stop_time, elapsed_time;

float A [N][N][N];

void relax();
void init();
void verify();

int main(int an, char **as) {
    int it = 0;
    gettimeofday(&start_time, NULL);
    init();
    for(it = 1; it <= itmax; it++) {
        eps = 0.;
        relax();
        if (eps < maxeps) {
            break;
        }
    }
    gettimeofday(&stop_time, NULL);
    timersub(&stop_time, &start_time, &elapsed_time);
    printf("\nMax error at iteration %d was %f\n", itmax, eps);
    printf("Total time was %f seconds\n", elapsed_time.tv_sec + elapsed_time.tv_usec / 1000000.0);
    verify();
    return 0;
}

void init() {
#pragma omp parallel for default(shared) private(j, i, k) shared(A)
    for (k = 0; k <= N - 1; k++)
        for (j = 0; j <= N - 1; j++)
            for (i = 0; i <= N - 1; i++)
                if (i == 0 || i == N - 1 || j == 0 || j == N - 1 || k == 0 || k == N - 1) {
                    A[i][j][k] = 0.;
                } else {
                    A[i][j][k] = (4. + i + j + k);
                }
}

void relax() {
#pragma omp parallel default(shared) private(i, j, k, b) shared(A) reduction(max: eps) 
{  
    #pragma omp for
    for (i = 1; i <= N - 2; i++)
		for (j = 1; j <= N - 2; j++)
			for (k = 1 + (i + j) % 2; k <= N - 2; k += 2) {
                b = w * ((A[i-1][j][k] + A[i+1][j][k] + A[i][j-1][k] + A[i][j+1][k] + A[i][j][k-1] + A[i][j][k+1]) / 6. - A[i][j][k]);
                eps = Max(fabs(b), eps);
                A[i][j][k] = A[i][j][k] + b;
            }
    #pragma omp for
    for (i = 1; i <= N - 2; i++)
		for (j = 1; j <= N - 2; j++)
			for (k = 1 + (i + j + 1) % 2; k <= N - 2; k += 2) {
                float b;
                b = w * ((A[i-1][j][k] + A[i+1][j][k] + A[i][j-1][k] + A[i][j+1][k] + A[i][j][k-1] + A[i][j][k+1]) / 6. - A[i][j][k]);
                A[i][j][k] = A[i][j][k] + b;
            }
}
}

void verify() {
    float s;
    s = 0.;
    #pragma omp parallel for default(shared) private(i, j, k) reduction(+:s)
	for (i = 0; i <= N - 1; i++)
	    for (j = 0; j <= N - 1; j++)
	        for (k = 0; k <= N - 1; k++) {
		        s = s + A[i][j][k] * (i + 1) * (j + 1) * (k + 1) / (N * N * N);
	        }
    printf("S = %f\n", s);
}
