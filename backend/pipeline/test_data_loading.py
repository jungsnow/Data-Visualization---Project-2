#!/usr/bin/env python
# coding: utf-8

"""
Test script for data loading pipeline without configuration dependencies
"""

import os
import json
from datetime import date, datetime, timedelta
from pymongo import MongoClient, DESCENDING
import pandas as pd
import numpy as np

# Direct configuration without pydantic
DB_URI = "mongodb+srv://gamer:mlgamer@cluster0.spxdw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "tftchamp"
TARGETNAME = "placement"

def handle_nas(df, default_date='2020-01-01'):
    """
    Handle NA values in dataframe
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    for f in df.columns:
        # integer
        if f in numeric_cols:
            df[f] = df[f].fillna(0)
        # dates
        elif df[f].dtype == '<M8[ns]':
            df[f] = df[f].fillna(pd.to_datetime(default_date))
        # boolean
        elif df[f].dtype == 'bool':
            df[f] = df[f].fillna(False)
        # string
        elif f in categorical_cols:
            df[f] = df[f].fillna('None')
    
    return df

def test_data_loading():
    """
    Test the data loading functionality
    """
    print("🔄 Testing Data Loading Pipeline...")
    
    try:
        # Connect to MongoDB
        client = MongoClient(DB_URI, tls=True, tlsAllowInvalidCertificates=True, 
                           connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
        db = client[DB_NAME]
        
        print("✅ MongoDB connection successful")
        
        # Check available collections
        collections = [col for col in db.list_collection_names() if 'matches_detail' in col]
        print(f"📊 Found {len(collections)} match collections:")
        
        for col in collections:
            count = db[col].count_documents({})
            print(f"   - {col}: {count} documents")
        
        if not collections:
            print("❌ No match data found. Run scraping first.")
            return False
            
        # Test data loading with the first available collection
        test_collection = collections[0]
        print(f"\n🧪 Testing data processing with {test_collection}...")
        
        # Load sample data
        sample_matches = list(db[test_collection].find().limit(5))
        
        if not sample_matches:
            print("❌ No sample data available")
            return False
            
        print(f"✅ Loaded {len(sample_matches)} sample matches")
        
        # Test data normalization
        print("🔄 Testing data normalization...")
        
        # Extract participants data
        participants_data = []
        for match in sample_matches:
            if 'info' in match and 'participants' in match['info']:
                for participant in match['info']['participants']:
                    participant['match_id'] = match['metadata']['match_id']
                    participant['game_datetime'] = match['info']['game_datetime']
                    participants_data.append(participant)
        
        if participants_data:
            # Create DataFrame
            df = pd.json_normalize(participants_data)
            print(f"✅ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
            
            # Test NA handling
            original_na_count = df.isnull().sum().sum()
            df_cleaned = handle_nas(df.copy())
            final_na_count = df_cleaned.isnull().sum().sum()
            
            print(f"✅ NA handling: {original_na_count} → {final_na_count} null values")
            
            # Show sample data
            print("\n📋 Sample processed data:")
            key_columns = ['puuid', 'placement', 'level', 'last_round']
            available_columns = [col for col in key_columns if col in df_cleaned.columns]
            if available_columns:
                print(df_cleaned[available_columns].head(3).to_string())
            else:
                print("Sample columns:", list(df_cleaned.columns)[:5])
                
        else:
            print("❌ No participant data found in matches")
            
        client.close()
        print("\n✅ Data Loading Pipeline Test Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in data loading test: {e}")
        return False

if __name__ == "__main__":
    test_data_loading()
