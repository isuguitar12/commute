import numpy as np

def weighting_function(df):
    # class_weights = {
    #     'Res 1 unit': 2,
    #     'Res 2-3 units': 2.5,
    #     'Apt 4+ units': 6,
    # #     '125 SRR',
    # #     '140 Res V Land',
    # #     '200 Agricultural',
    # #     '211 Rural Vacant Land',
    #     'Commercial': 2,
    #     'Industrial': 1.5,
    # #     '320 Q Golf Course',
    #     'Schools-Public': 1,
    # #     '911 Cemetery-Public',
    # #     '912 Cemetery-Private',
    # #     '915 Church',
    # #     '916 Church-Residence',
    # #     '917 Church-Other Res',
    # #     '918 Church - Other',
    # #     '925 Trans Housing',
    # #     '931 Charit Inst',
    # #     '940 Wetlands',
    # #     '941 ForestParkRefuge',
    # #     '942 Indian Resrv',
    # #     '951 Federal Property',
    # #     '952 State Property',
    # #     '955 Co Srvc Other',
    # #     '956 Muni Srvc Ent',
    # #     '958 Muni Srvc Other',
    # #     '962 T E Misc Co D 3',
    # #     '981 State Acquired',
    # #     '982 State Admin-DNR',
    # #     '983 Co Admin-TaxForf',
    # #     '990 InLieuTx Co D 1',
    # }
    class_weights = {
        'AGRICULTURAL': 0,
        'RESIDENTIAL SINGLE FAMILY': 1,
        'COMMERCIAL / GOLF COURSE': 0,
        'TAX FORFEIT': 0,
        'RESIDENTIAL DUPLEXES': 2,
        'MANUFACTURED HOME PARK': 15,
        'APARTMENTS / COOP': 15,
        'CONDOMINIUMS': 15,
        'UTILITY PROPERTY': 0,
        'INDUSTRIAL': 1.5,
        'Res 1 unit': 1,
        'T E Misc Co D 10': 0,
        'Muni Srvc Ent': 0,
        'Commercial': 1,
        'Res V Land': 0.5,
        'Wetlands': 0,
        'Muni Srvc Other': 0,
        'SRR': 0,
        'Federal Property': 0.5,
        'Co Srvc Other': 0,
        'Res 2-3 units': 5,
        'Industrial': 1.5,
        'MH Park Class I': 0,
        'Schools-Public': 1.5,
        'T E Misc Co D 1': 0,
        'Sp Tax District': 0,
        'Charit Inst-Res': 0
    }

    year_weights = lambda x: np.exp((x - 2020) / 10)
    use_weight = df["USECLASS1"].map(lambda x: class_weights.get(x, 0)).values
    return use_weight #* year_weights(df["YEAR_BUILT"].values)
