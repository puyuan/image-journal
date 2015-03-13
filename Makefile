createdb: createdb.c
	gcc -g -o createdb createdb.c -lexif -lsqlite3  `pkg-config --cflags --libs glib-2.0`
