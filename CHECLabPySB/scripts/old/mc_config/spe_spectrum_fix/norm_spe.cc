#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cmath>

int read_table3 (const char *fname, int maxrow, double *col1, double *col2, double *col3);

int read_table3 (const char *fname, int maxrow, double *col1, double *col2, double *col3)
{
   FILE *f;
   double x, y, z;
   char line[1024];
   int iline = 0, n=0;
   
   if ( strcmp(fname,"-") == 0 )
      f = stdin;
   else if ( (f = fopen(fname,"r")) == NULL )
   {
      perror(fname);
      return -1;
   }
   
   while ( fgets(line,sizeof(line)-1,f) != NULL )
   {
      iline++;
      char *s = strchr(line,'#');
      if ( s != 0 )
         *s = '\0';
      int l = strlen(line);
      for ( int i=l; i>0; i-- )
      {
         if ( line[i-1] == ' ' || line[i-1] == '\t' || line[i-1] == '\n' )
            line[i-1] = '\0';
         else
            break;
      }

      if ( line[0] == '\0' )
      	 continue;
      
      if ( sscanf(line,"%lf %lf %lf",&x,&y,&z) != 3 )
      {
      	 fprintf(stderr,"Error in line %d of file %s\n",iline,fname);
         if ( f != stdin )
	    fclose(f);
	 return -1;
      }
      if ( n >= maxrow )
      {
      	 fprintf(stderr,"Too many entries in file %s (max=%d)\n",fname,maxrow);
         if ( f != stdin )
	    fclose(f);
	 return -1;
      }
      col1[n] = x;
      col2[n] = y;
      col3[n] = z;
      n++;
   }
   
   printf("Table with %d rows has been read from file %s\n",n,fname);

   if ( f != stdin )
      fclose(f);

   return n;
}

#define MAX_SPE 10000

int main(int argc, char **argv)
{
   double x[MAX_SPE], spe[MAX_SPE], spe_ap[MAX_SPE];
   int n = 0;
   int i, j;
   double i_spe = 0.;
   double i_xspe = 0.;
   double norm_x, norm_spe;
   double sumw = 0., sumns = 0., sumns2 = 0., below01 = 0., below02 = 0.;
   double mean = 0., x_peak = 0., c_rms = 0., peak = -1.;

   if ( argc != 2 )
   {
      fprintf(stderr,"Normalize a singe-p.e. amplitude distribution to mean amplitude of 1.0\n");
      fprintf(stderr,"Syntax: %s filename\n", argv[0]);
      exit(1);
   }
   
   if ( (n = read_table3(argv[1],MAX_SPE,x,spe,spe_ap)) <= 0 )
      exit(1);

   for (i=1; i<n; i++)
   {
      if ( x[i] <= x[i-1] )
         continue;
      i_spe += (x[i]-x[i-1])*0.5*(spe[i]+spe[i-1]);
      i_xspe += 0.5*(x[i]+x[i-1]) * (x[i]-x[i-1])*0.5*(spe[i]+spe[i-1]);
   }

    printf("# i_spe = %5.3f, i_xspe %5.3f\n", i_spe, i_xspe);

   if ( i_spe <= 0. || i_xspe <= 0. )
   {
      fprintf(stderr,"Cannot normalize\n");
      exit(1);
   }

   norm_x = i_spe / i_xspe;
   norm_spe = 1./(i_spe*norm_x);
   fprintf(stderr,"Scaling x axis by factor %g\n", norm_x);
   fprintf(stderr,"Scaling y axis by factor %g\n", norm_spe);

   for (j=0, i=1; i<n; i++)
   {
      double px, dx, y;
      if ( x[i] <= x[j] )
         continue;
      if ( (spe[j]+spe[i]) == 0. )
         continue;
      px = (x[j]*spe[j] + x[i]*spe[i]) / (spe[j]+spe[i]) * norm_x;
      dx = (x[i]-x[j]) * norm_x;
      y = 0.5*(spe[i]+spe[j]) * norm_spe;
      if ( px < 0.1 )
         below01 += y*dx;
      if ( px < 0.2 )
         below02 += y*dx;
      sumw += y*dx;
      sumns += px*y*dx;
      sumns2 += px*px*y*dx;
      if ( y > peak )
      {
         peak = y;
         x_peak = px;
      }
      j = i;
//      printf("? %f %f %f\n",px,dx,y);
   }
   
   if ( sumw > 0. )
   {
      mean = sumns/sumw;
      c_rms = sqrt(sumns2/sumw-mean*mean)/mean;
      below01 /= sumw;
      below02 /= sumw;
   }

//   printf("# Mean(prompt) = %5.3f, peak at %5.3f (sum=%5.3f)\n", mean, x_peak, sumw);
//   printf("# Fraction of events below 10%% of mean: %5.3f\n", below01);
//   printf("# Fraction of events below 20%% of mean: %5.3f\n", below02);
//   printf("# Sqrt(Excess noise factor): %5.3f, ENF = %5.3f\n", sqrt(1.+c_rms*c_rms),1+c_rms*c_rms);
//   printf("# Note: collection efficiency losses should be included in low amplitude signals.\n\n");
//
//   for (i=1; i<n; i++)
//   {
//      printf("%8.6f\t%-12.5g\t%-12.5g\t\t%%%%%% original: \t%8.6f\t%-12.5g\t%-12.5g\n",
//         x[i]*norm_x, spe[i]*norm_spe, spe_ap[i]*norm_spe,
//         x[i], spe[i], spe_ap[i]);
//   }

   for (i=1; i<n; i++)
   {
      printf("%8.6f\t%-12.5g\t%-12.5g\n",
         x[i]*norm_x, spe[i]*norm_spe, spe_ap[i]*norm_spe);
   }

   return 0;
}
