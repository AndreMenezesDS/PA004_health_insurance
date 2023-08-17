import pickle
import numpy as np
import pandas as pd

class HealthInsurance:

    def __init__(self):
        self.home_path = ''
        self.ss_premium_scaler =        pickle.load(open(self.home_path + 'src/features/ss_premium_scaler.pkl', 'rb'))
        self.ss_premium_day_scaler =    pickle.load(open(self.home_path + 'src/features/ss_premium_day_scaler.pkl', 'rb'))
        self.ss_premium_age_scaler =    pickle.load(open(self.home_path + 'src/features/ss_premium_age_scaler.pkl', 'rb'))
        self.mms_age_scaler =           pickle.load(open(self.home_path + 'src/features/mms_age_scaler.pkl', 'rb'))
        self.mms_vintage_scaler =       pickle.load(open(self.home_path + 'src/features/mms_vintage_scaler.pkl', 'rb'))
        self.mms_vintage_age_scaler =   pickle.load(open(self.home_path + 'src/features/mms_vintage_age_scaler.pkl', 'rb'))
        self.fe_region_scaler =         pickle.load(open(self.home_path + 'src/features/fe_region_scaler.pkl', 'rb'))
        self.te_channel_scaler =        pickle.load(open(self.home_path + 'src/features/te_channel_scaler.pkl', 'rb'))

    def data_cleaning(self, df1):
        #data formating/cleaning
        df1['region_code'] = df1['region_code'].astype(np.int64)
        df1['policy_sales_channel'] = df1['policy_sales_channel'].astype(np.int64)
        df1['vehicle_damage'] = df1['vehicle_damage'].apply(lambda x: 1 if x == 'Yes' else 0)

        return df1

    def reorder_data(self, df2):
        # Reorder/Rename Columns
        reorder_columns = ['id', 'age', 'region_code', 'policy_sales_channel',
                           'previously_insured', 'annual_premium', 'vintage',
                           'driving_license', 'vehicle_age', 'vehicle_damage', 'response']

        df2 = df2.reindex(columns=reorder_columns)

        return df2
    
    def feature_engineering(self, df3):
        #vehicle_age_score
        vehicle_age_dict = {'< 1 Year': 1,
                            '1-2 Year': 2,
                            '> 2 Years': 3}
        df3['vehicle_age_score'] = df3['vehicle_age'].map(vehicle_age_dict)
        
        #annual premium paid per day
        df3['annual_premium_per_day'] = df3['annual_premium']/df3['vintage']

        #annual premium divided per age
        df3['annual_premium_per_age'] = df3['annual_premium']/df3['age']

        #vintage_per_age
        df3['vintage_per_age'] = df3['vintage']/df3['age']

        #Creation of the dictionary that will designate each policy sales channel to its score
        aux9_2 = df3[['policy_sales_channel', 'response']].groupby('policy_sales_channel').value_counts(normalize=True).reset_index()
        aux9_2 = aux9_2.drop(aux9_2[aux9_2['response'] == 0].index).sort_values(0)
        aux9_2['scored_sales_channel'] = aux9_2[0].apply(lambda x: 5 if x > 0.3 else
                                                         4 if (x <= 0.3) & (x > 0.25) else
                                                         3 if (x <= 0.25) & (x > 0.2) else
                                                         2 if (x <= 0.2) & (x > 0.1) else 1)
        scored_sales_channel = {channel: score for channel, score in zip(aux9_2['policy_sales_channel'], aux9_2['scored_sales_channel'])}

        #Appending the scored channel to the original dataframe, on its respective ids
        df3['scored_sales_channel'] = df3['policy_sales_channel'].map(scored_sales_channel)
        df3['scored_sales_channel'].fillna(1, inplace=True)
        df3['scored_sales_channel']= df3['scored_sales_channel'].astype(np.int64)

        #Creation of the dictionary that will designate each region code to its score
        aux8_2 = df3[['region_code', 'vehicle_damage', 'response']].groupby('region_code').value_counts(normalize=True).reset_index()
        aux8_2 = aux8_2.loc[(aux8_2['response'] == 1) & (aux8_2['vehicle_damage'] == 1), :].sort_values(0)
        aux8_2['region_score'] = aux8_2[0].apply(lambda x: 4 if x >= 0.15 else
                                                3 if (x < 0.15) & (x >= 0.10) else
                                                2 if (x < 0.10) & (x >= 0.05) else 1)
        region_insured_dict = {region: score for region, score in zip(aux8_2['region_code'], aux8_2['region_score'])}

        #Appending the scored regions to the original dataframe, on its respective ids
        df3['region_score'] = df3['region_code'].map(region_insured_dict)
        df3['region_score'].fillna(1, inplace=True)
        df3['region_score'] = df3['region_score'].astype(np.int64)


        reorder_columns = ['id', 'age', 'region_code', 'policy_sales_channel',
            'previously_insured', 'annual_premium', 'vintage',
            'driving_license', 'vehicle_age', 'vehicle_damage',
            'scored_sales_channel', 'vehicle_age_score', 'region_score',
            'annual_premium_per_day', 'annual_premium_per_age',
            'vintage_per_age', 'response']

        df3 = df3.reindex(columns=reorder_columns)

        return df3
    
    
    def data_preparation(self, df4):
        #annual_premium
        df4['annual_premium'] = self.ss_premium_scaler.transform(df4[['annual_premium']].values)

        #annual_premium_per_day
        df4['annual_premium_per_day'] = self.ss_premium_day_scaler.transform(df4[['annual_premium_per_day']].values)

        #annual_premium_per_age
        df4['annual_premium_per_age'] = self.ss_premium_age_scaler.transform(df4[['annual_premium_per_age']].values)

        #age
        df4['age'] = self.mms_age_scaler.transform(df4[['age']].values)

        #vintage
        df4['vintage'] = self.mms_vintage_scaler.transform(df4[['vintage']].values)

        #vintage_per_age
        df4['vintage_per_age'] = self.mms_vintage_age_scaler.transform(df4[['vintage_per_age']].values)

        ##annual_premium
        #df4['annual_premium'] = (df4['annual_premium'] - df4['annual_premium'].mean()) / df4['annual_premium'].std()

        ##annual_premium_per_day
        #df4['annual_premium_per_day'] = (df4['annual_premium_per_day'] - df4['annual_premium_per_day'].mean()) / df4['annual_premium_per_day'].std()

        ##annual_premium_per_age
        #df4['annual_premium_per_age'] = (df4['annual_premium_per_age'] - df4['annual_premium_per_age'].mean()) / df4['annual_premium_per_age'].std()

        ##age
        #df4['age'] = (df4['age'] - df4['age'].min()) / (df4['age'].max() - df4['age'].min())

        ##vintage
        #df4['vintage'] = (df4['vintage'] - df4['vintage'].min()) / (df4['vintage'].max() - df4['vintage'].min())

        ##vintage_per_age
        #df4['vintage_per_age'] = (df4['vintage_per_age'] - df4['vintage_per_age'].min()) / (df4['vintage_per_age'].max() - df4['vintage_per_age'].min())

        #region_code - Frequency Encoding
        df4.loc[:, 'region_code'] = df4['region_code'].map(self.fe_region_scaler)

        #policy_sales_channel - Mean Target Encoding
        df4.loc[:, 'policy_sales_channel'] = df4['policy_sales_channel'].map(self.te_channel_scaler)    

        #NOTA -> For Vehicle Age, the created feature 'vehicle_age_score' was maintained, given that it functions as an ordinal encoder for 'vehicle_age'.
        #vehicle_age - One Hot Encoding
        df4 = pd.get_dummies(df4, prefix='vehicle_age', columns=['vehicle_age'])

        #cols_selected = [ 'annual_premium_per_day', 'vintage_per_age', 'vintage',
        #                  'annual_premium_per_age', 'annual_premium', 'age',
        #                  'vehicle_damage', 'region_code', 'policy_sales_channel',
        #                  'scored_sales_channel', 'region_score', 'vehicle_age_score']

        cols_selected = ['vintage', 'annual_premium', 'age', 'region_code', 
                         'vehicle_damage', 'policy_sales_channel', 'previously_insured']
        
        return df4[cols_selected]

    def get_prediction(self, model, original_data, test_data):
        #model prediction
        pred = model.predict_proba(test_data)

        #join prediction into original data
        original_data['score'] = pred[:, 1].tolist()

        return original_data.to_json( orient='records', date_format='iso')