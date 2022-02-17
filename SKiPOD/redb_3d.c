#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>
#define  Max(a,b) ((a)>(b)?(a):(b))

#define SMALL_DATASET

# if !defined(MINI_DATASET) && !defined(SMALL_DATASET) && !defined(MEDIUM_DATASET) && !defined(LARGE_DATASET)
#define LARGE_DATASET
# endif

# ifdef MINI_DATASET
#define  N (2 * 2 * 2 + 2)
# endif

# ifdef SMALL_DATASET
#define  N (2 * 2 * 2 * 2 * 2 * 2 + 2)
# endif

# ifdef MEDIUM_DATASET
#define  N (2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 + 2)
# endif

# ifdef LARGE_DATASET
#define  N (2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 * 2 + 2)
# endif

float maxeps = 0.1e-7;
int itmax = 100;
int i,j,k;
float w = 0.5;
float eps;
struct timeval start_time, stop_time, elapsed_time;

float A [N][N][N];
double bench_t_start, bench_t_end;

static
double rtclock()
{
    struct timeval Tp;
    int stat;
    stat = gettimeofday (&Tp, NULL);
    if (stat != 0)
      printf ("Error return from gettimeofday: %d", stat);
    return (Tp.tv_sec + Tp.tv_usec * 1.0e-6);
}

void bench_timer_start()
{
  bench_t_start = rtclock();
}

void bench_timer_stop()
{
  bench_t_end = rtclock ();
}

void bench_timer_print()
{
  printf ("Time in seconds = %0.6lf\n", bench_t_end - bench_t_start);
}

void relax();
void init();
void verify(); 

int main(int an, char **as) {
	int it;
    bench_timer_start();
	init();
	for(it = 1; it <= itmax; it++) {
		eps = 0.;
		relax();
		if (eps < maxeps) {
			break;
		}
	}
	verify();
    bench_timer_stop();
    bench_timer_print();
	return 0;
}

void init() {
{	
	for(k = 0; k <= N - 1; k++) 
		for(j = 0; j <= N - 1; j++)
			for(i = 0; i <= N - 1; i++)
				if(i == 0 || i == N - 1 || j == 0 || j == N - 1 || k == 0 || k == N - 1) { 
					A[i][j][k] = 0.;
				}
				else {
					A[i][j][k] = (4. + i + j + k);
				}
}
} 


void relax() {
{
	for(k = 1; k <= N - 2; k++)
		for(j = 1; j <= N - 2; j++)
			for(i = 1 + (k + j) % 2; i <= N - 2; i += 2){ 
				float b;
				b = w * ((A[i-1][j][k] + A[i+1][j][k] + A[i][j-1][k] + A[i][j+1][k] + A[i][j][k-1] + A[i][j][k+1]) / 6. - A[i][j][k]);
				eps = Max(fabs(b), eps);
				A[i][j][k] = A[i][j][k] + b;
			}

	for(k = 1; k <= N - 2; k++)
		for(j = 1; j <= N - 2; j++)
			for(i = 1 + (k + j + 1) % 2; i <= N - 2; i += 2) {
				float b;
				b = w * ((A[i-1][j][k] + A[i+1][j][k] + A[i][j-1][k] + A[i][j+1][k] + A[i][j][k-1] + A[i][j][k+1]) / 6. - A[i][j][k]);
				A[i][j][k] = A[i][j][k] + b;
			}

}
}

void verify() { 
	float s;
	s = 0.;
{	
	for(k = 0; k <= N - 1; k++)
		for(j = 0; j <= N - 1; j++)
			for(i = 0; i <= N - 1; i++) {
				s = s + A[i][j][k] * (i + 1) * (j + 1) * (k + 1) / (N * N * N);
			}
}
	printf("S = %f\n", s);
}
