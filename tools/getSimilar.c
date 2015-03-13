#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sqlite3.h>
#include <time.h>
#include <string.h>
#include <locale.h>

int curTimestamp=123;
struct tm tm;
time_t t;
int count=0;
char * str;
char * collection[400];

void printCollection(){
  int i=0;
  for (i=0; i< count; i++){
    printf("%s\n", collection[i]);
  }


}


static int callback(void *NotUsed, int argc, char **argv, char **azColName){
  int i;
  time_t epoch;
  char *fname=argv[4];

  if( access( fname, F_OK ) == -1 ) {
    // file doesn't exist
    return 0;
  } 


//   printf("%s\n",argv[0]);
//   printf("%s\n",argv[4]);
  // can't parse time
  if(!strptime(argv[0], "%Y:%m:%d %H:%M:%S", &tm)){ 
//    printf("cant parse\n");
    return 0;

}

  //    scanf("%d%d%d:%d%d:%d%d %d%d:%d%d:%d%d", str );

  epoch=mktime(&tm);
  if (abs((int)epoch -  curTimestamp) >= 10*1){    //printf("current time:%d and current timestamp %d", (int) epoch, curTimestamp);
    if (count>1)
      printCollection();
    count=0;
  }
  // printf("%s = %s\n", azColName[0], argv[0] ? argv[0] : "NULL");
  char *str=malloc(sizeof(char)*300);
  strcpy(str, argv[4]);
  collection[count]=str;
  curTimestamp=(int) epoch;
  count++;
  return 0;

  /*
     printf("year: %d; month: %d; day: %d;\n",
     tm.tm_year, tm.tm_mon, tm.tm_mday);
   i  printf("hour: %d; minute: %d; second: %d\n",
     tm.tm_hour, tm.tm_min, tm.tm_sec);
     printf("week day: %d; year day: %d\n", tm.tm_wday, tm.tm_yday);

     printf("epoch %d\n", (int) epoch);
     */
}


int main(){
 setlocale(LC_ALL, "");
  sqlite3 *db;
  int rc;
  char *zErrMsg = 0;
  str=malloc(sizeof(char)*(1000));
  rc=sqlite3_open("../data/images.sqlite", &db);

  if( rc ){
    fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return(1);
  }
  rc = sqlite3_exec(db,"select * from images order by CreateDate desc"  , callback, 0, &zErrMsg);
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", zErrMsg);
    sqlite3_free(zErrMsg);
  }
  sqlite3_close(db);
  return 0;

}
