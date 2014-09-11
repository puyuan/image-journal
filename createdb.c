/*
 * libexif example program to display the contents of a number of specific
 * EXIF and MakerNote tags. The tags selected are those that may aid in
 * identification of the photographer who took the image.
 *
 * Placed into the public domain by Dan Fandrich
 */

#include <unistd.h>
#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libexif/exif-data.h>
#include <glib-2.0/glib.h>
#include <locale.h>

int readImage(char *path);
GHashTable  *hash;
sqlite3 *db;
int count;
/* Remove spaces on the right of the string */
static void trim_spaces(char *buf)
{
  char *s = buf-1;
  for (; *buf; ++buf) {
    if (*buf != ' ')
      s = buf;
  }
  *++s = 0; /* nul terminate the string on the first of the final spaces */
}

/* Show the tag name and contents if the tag exists */
static void show_tag(ExifData *d, ExifIfd ifd, ExifTag tag)
{
  /* See if this tag exists */
  ExifEntry *entry = exif_content_get_entry(d->ifd[ifd],tag);
  if (entry) {
    char buf[1024];

    /* Get the contents of the tag in human-readable form */
    exif_entry_get_value(entry, buf, sizeof(buf));

    /* Don't bother printing it if it's entirely blank */
    trim_spaces(buf);
    if (*buf) {
      printf("%s: %s\n", exif_tag_get_name_in_ifd(tag,ifd), buf);
    }
  }
}
/* Fetch the tag name and contents if the tag exists */
static char * fetch_tag(ExifData *d, ExifIfd ifd, ExifTag tag)
{
  /* See if this tag exists */
  ExifEntry *entry = exif_content_get_entry(d->ifd[ifd],tag);
  if (entry) {
    int size=sizeof(char) * 1024;
    char *buf=malloc(size);
    strcpy(buf, "test");

    /* Get the contents of the tag in human-readable form */
    exif_entry_get_value(entry, buf, size);

    /* Don't bother printing it if it's entirely blank */
    trim_spaces(buf);
    if (*buf) {
      return buf;
    }

  }
  return NULL;
}

createDB(){


char * str="create table if not exists images \
         (CreateDate text primary key, \
	  GPSLatitude real, \
GPSLongitude   real,  \
	GPSAltitude    real ,\
	SourceFile   text \
    )";
   
int rc;
  rc = sqlite3_exec(db,str , 0, 0, 0);

  if( rc!=SQLITE_OK ){
    printf("DB might be created already\n");
  }
}

/* Show the given MakerNote tag if it exists */
static void show_mnote_tag(ExifData *d, unsigned tag)
{
  ExifMnoteData *mn = exif_data_get_mnote_data(d);
  if (mn) {
    int num = exif_mnote_data_count(mn);
    int i;

    /* Loop through all MakerNote tags, searching for the desired one */
    for (i=0; i < num; ++i) {
      char * buf= (char *) malloc(sizeof(char)*1024);
      if (exif_mnote_data_get_id(mn, i) == tag) {
        if (exif_mnote_data_get_value(mn, i, buf, sizeof(buf))) {
          /* Don't bother printing it if it's entirely blank */
          trim_spaces(buf);
          if (*buf) {
            printf("%s: %s\n", exif_mnote_data_get_title(mn, i),
                buf);
          }
        }
      }
    }
  }
}


void insert(char *key){
  char *new_str=malloc(sizeof(char)*1024);
  strcpy(new_str, key);
  g_hash_table_insert(hash, new_str, "hi");

}

void testPopen(){

  FILE *fp;
  char  path[1024];
  char command[100];
  
  sprintf(command,"find '%s' -iname *.jpg",getenv("image_folder")  );

  fp = popen(command, "r");
  while (fgets(path, sizeof(path)-1, fp)!=NULL){
    strtok(path, "\n");
    //printf("reading %s\n", path);
    //    readImage(path);
    char *key=g_hash_table_lookup(hash, path);
    if (key==NULL){
      printf("new file: %s\n", path);
      readImage(path);

    }


  }

  pclose(fp);


}

int readImage(char *path){

  ExifData *ed;
  ExifEntry *entry;
  /* Load an ExifData object from an EXIF file */
  ed = exif_data_new_from_file(path);
  if (!ed) {
    printf("File not readable or no EXIF data in file %s\n", path);
    return 2;
  }

  /* Show all the tags that might contain information about the
   * photographer
   */
  char * a, *b, *c, *d, *e;
  /*
  show_tag(ed, EXIF_IFD_EXIF, EXIF_TAG_PIXEL_X_DIMENSION);
  show_tag(ed, EXIF_IFD_0, EXIF_TAG_DATE_TIME);
  show_tag(ed, EXIF_IFD_GPS, EXIF_TAG_GPS_LONGITUDE );
  show_tag(ed, EXIF_IFD_GPS, EXIF_TAG_GPS_LATITUDE );
  */
  a=fetch_tag(ed, EXIF_IFD_EXIF, EXIF_TAG_PIXEL_X_DIMENSION);
  b=fetch_tag(ed, EXIF_IFD_0, EXIF_TAG_DATE_TIME);
  printf("this is%s \n", b);
  if (b==NULL){
    b=malloc(sizeof(char)*1024);
    sprintf(b, "jumbo%d%d", time(NULL), count);
    count++;
  }

  c=fetch_tag(ed, EXIF_IFD_GPS, EXIF_TAG_GPS_LONGITUDE );
  d=fetch_tag(ed, EXIF_IFD_GPS, EXIF_TAG_GPS_LATITUDE );
  e=fetch_tag(ed, EXIF_IFD_GPS, EXIF_TAG_GPS_ALTITUDE );
  insertImageRecord(b, c, d,e, path);
  
  /* These are much less likely to be useful */
  show_tag(ed, EXIF_IFD_EXIF, EXIF_TAG_USER_COMMENT);
  show_tag(ed, EXIF_IFD_0, EXIF_TAG_IMAGE_DESCRIPTION);
  show_tag(ed, EXIF_IFD_1, EXIF_TAG_IMAGE_DESCRIPTION);

  /* A couple of MakerNote tags can contain useful data.  Read the
   * manufacturer tag to see if this image could have one of the recognized
   * MakerNote tags.
   */
  entry = exif_content_get_entry(ed->ifd[EXIF_IFD_0], EXIF_TAG_MAKE);
  if (entry) {
    char buf[64];

    /* Get the contents of the manufacturer tag as a string */
    if (exif_entry_get_value(entry, buf, sizeof(buf))) {
      trim_spaces(buf);

      if (!strcmp(buf, "Canon")) {
        show_mnote_tag(ed, 9); /* MNOTE_CANON_TAG_OWNER */

      } else if (!strcmp(buf, "Asahi Optical Co.,Ltd.") || 
          !strcmp(buf, "PENTAX Corporation")) {
        show_mnote_tag(ed, 0x23); /* MNOTE_PENTAX2_TAG_HOMETOWN_CITY */
      }
    }
  }

  /* Free the EXIF data */
  exif_data_unref(ed);


}


static int processResult(void *NotUsed, int argc, char **argv, char **azColName){

  insert(argv[4]);
 // printf("inserting %s\n", argv[4]);
  return 0;
}


int querydb(){
  int rc;
  char *zErrMsg = 0;

  rc = sqlite3_exec(db,"select * from images order by CreateDate desc"  , processResult, 0, &zErrMsg);
  printf("everythin completed here\n\n");
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", zErrMsg);
    sqlite3_free(zErrMsg);
  }
  return 0;
}

int insertImageRecord(char *createDate, char *gpsLatitude, char * gpsLongitude, char * gpsAltitude, char * sourceFile){

  char str[1024];
  char *zErrMsg = 0;
  sprintf(str, "insert into images values ('%s', '%s', '%s' ,'%s', '%s')", createDate, gpsLatitude, gpsLongitude, gpsAltitude, sourceFile);

//  printf(str);
  int rc=sqlite3_exec(db, str , 0, 0, &zErrMsg);

  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", zErrMsg);
  if (strcmp("UNIQUE constraint failed: images.CreateDate", zErrMsg)==0){
	  char num[4];
	  char temp[30];
	  strcpy(temp, createDate);
	  sprintf(num,"%d", count );
	  createDate=strcat(temp, num );
	  count++;
	
	  sprintf(str, "insert into images values ('%s', '%s', '%s' ,'%s', '%s')", createDate, gpsLatitude, gpsLongitude, gpsAltitude, sourceFile);
	  rc=sqlite3_exec(db, str , 0, 0, &zErrMsg);
			}
	
    sqlite3_free(zErrMsg);
  }
}

int main(int argc, char **argv)
{

  /*
     if (argc < 2) {
     printf("Usage: %s image.jpg\n", argv[0]);
     printf("Displays tags potentially relating to ownership "
     "of the image.\n");
     return 1;
     }

*/
  setlocale(LC_ALL, "");
  int rc;
  rc=sqlite3_open("data/images.sqlite", &db);
  if( rc ){
    fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return(1);
  }

  hash = g_hash_table_new(g_str_hash, g_str_equal);
  createDB();
  querydb();
  testPopen();
  sqlite3_close(db);
}
