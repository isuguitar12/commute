#include <stdio.h>
#include <stdlib.h>
#include <proj.h>
#include <shapefil.h>
#include "../../include/PathFinder/process.h"

#define BOOL char
#define FALSE 0
#define TRUE 1

void alterLongLat(DBFHandle dbfH) {
    double currLong, currLat, newLong, newLat;
    int i;
    
    PJ_CONTEXT *C;
    PJ *P;
    PJ* P_for_GIS;
    PJ_COORD a, b;
    
    C = proj_context_create();

    P = proj_create_crs_to_crs (C,
                                "EPSG:26915",
                                "EPSG:4326",
                                NULL);

    if (0==P) {
        fprintf(stderr, "Oops\n");
        // return 1;
    }

    /* This will ensure that the order of coordinates for the input CRS */
    /* will be longitude, latitude, whereas EPSG:4326 mandates latitude, */
    /* longitude */
    // P_for_GIS = proj_normalize_for_visualization(C, P);
    // if( 0 == P_for_GIS )  {
    //     fprintf(stderr, "Oops\n");
    //     // return 1;
    // }
    // proj_destroy(P);
    // P = P_for_GIS;


    int records = DBFGetRecordCount(dbfH);

    int longLoc = DBFGetFieldIndex(dbfH, "LONGITUDE");
    int latLoc = DBFGetFieldIndex(dbfH, "LATITUDE");
    for (i = 0; i < records; ++i) {
        currLong = DBFReadDoubleAttribute(dbfH, i, longLoc);
        currLat = DBFReadDoubleAttribute(dbfH, i, latLoc);
        printf("Longitude: %lf Latitude: %lf\n", currLong, currLat);
        if (currLong > 0) {
            a = proj_coord (currLong, currLat, 0, 0);
            b = proj_trans (P, PJ_FWD, a);
            newLong = b.lp.phi;
            newLat = b.lp.lam;
            DBFWriteDoubleAttribute(dbfH, i, longLoc, newLong);
            DBFWriteDoubleAttribute(dbfH, i, latLoc, newLat);
        } 
        // printf("Longitude: %lf Latitude: %lf\n", longlat_array[i][0], longlat_array[i][1]);
    }
    printf("here");
    // geoConversion(longlat_array, records);
    // for (i = 0; i < records; ++i) {
    //     printf("Longitude: %lf Latitude: %lf\n", longlat_array[i][0], longlat_array[i][1]);
    // }
    // free(longlat_array);
    /* Clean up */
    proj_destroy (P);
    proj_context_destroy (C); /* may be omitted in the single threaded case */
}

int main ( int argc, char *argv[] )
{

    DBFHandle dbfH = DBFOpen( argv[1], "rb+" );
    int records = DBFGetRecordCount(dbfH);
    printf( "%d files found\n", records);
    int fieldLen = DBFGetFieldCount(dbfH);
    int i;
    DBFFieldType eType;
    char fieldName[12];
    for (i = 0; i < fieldLen; ++i) {
        printf("\n");
        eType = DBFGetFieldInfo(dbfH, i, fieldName, NULL, NULL);
        printf("Field Name: %s\n", fieldName);
        if( eType == FTString )
            printf( "%d: String\n", i);
        else if( eType == FTInteger )
            printf( "%d: Integer\n", i);
        else if( eType == FTDouble )
            printf( "%d: Double\n", i);
    }
    alterLongLat(dbfH);
    DBFClose(dbfH);
    return 0;
}