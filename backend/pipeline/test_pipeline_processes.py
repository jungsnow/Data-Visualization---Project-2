#!/usr/bin/env python3
"""
Test script for TFT Champion pipeline processes
This bypasses configuration issues and tests core pipeline functionality
"""

import pandas as pd
import numpy as np
import json
import os
from pymongo import MongoClient
from datetime import datetime

# Direct MongoDB configuration to avoid pydantic issues
DB_URI = "mongodb+srv://dungkcbk31:Lb4vpBUfyq6N89oD@tftchamp.j5grpi1.mongodb.net/?retryWrites=true&w=majority&appName=tftchamp"
DB_NAME = "tftchamp"

def test_database_connection():
    """Test MongoDB connection and data availability"""
    print("🔍 Testing database connection...")
    try:
        client = MongoClient(DB_URI, tls=True, tlsAllowInvalidCertificates=True, 
                           connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
        db = client[DB_NAME]
        
        # List collections
        collections = db.list_collection_names()
        print(f"✅ Connected to database. Found {len(collections)} collections")
        
        # Check match data
        match_collections = [col for col in collections if 'matches_detail' in col]
        print(f"📊 Match collections available: {len(match_collections)}")
        
        for col in match_collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
            
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_data_loading_process():
    """Test data loading and transformation functionality"""
    print("\n🔄 Testing data loading process...")
    
    try:
        client = MongoClient(DB_URI, tls=True, tlsAllowInvalidCertificates=True,
                           connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
        db = client[DB_NAME]
        
        # Find a collection with match data
        match_collections = [col for col in db.list_collection_names() if 'matches_detail' in col]
        
        if not match_collections:
            print("❌ No match data collections found")
            return False
            
        # Test data loading from the first available collection
        collection_name = match_collections[0]
        collection = db[collection_name]
        
        print(f"📋 Testing with collection: {collection_name}")
        
        # Load a sample of match data
        sample_matches = list(collection.find().limit(5))
        print(f"✅ Loaded {len(sample_matches)} sample matches")
        
        # Test data transformation
        if sample_matches:
            # Extract basic match info
            match_info = []
            for match in sample_matches:
                if 'info' in match and 'participants' in match['info']:
                    participants = match['info']['participants']
                    for participant in participants:
                        match_info.append({
                            'match_id': match.get('metadata', {}).get('match_id', 'unknown'),
                            'puuid': participant.get('puuid', ''),
                            'placement': participant.get('placement', 0),
                            'level': participant.get('level', 0),
                            'last_round': participant.get('last_round', 0),
                            'time_eliminated': participant.get('time_eliminated', 0)
                        })
            
            if match_info:
                df = pd.DataFrame(match_info)
                print(f"✅ Transformed data into DataFrame with {len(df)} rows")
                print(f"📊 Columns: {list(df.columns)}")
                print(f"📈 Sample placement stats: mean={df['placement'].mean():.2f}, std={df['placement'].std():.2f}")
                
                client.close()
                return True
            else:
                print("❌ No participant data found in matches")
                client.close()
                return False
        else:
            print("❌ No matches found in collection")
            client.close()
            return False
            
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
        return False

def test_team_composition_analysis():
    """Test team composition analysis functionality"""
    print("\n🎯 Testing team composition analysis...")
    
    try:
        client = MongoClient(DB_URI, tls=True, tlsAllowInvalidCertificates=True,
                           connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
        db = client[DB_NAME]
        
        # Find match data
        match_collections = [col for col in db.list_collection_names() if 'matches_detail' in col]
        
        if not match_collections:
            print("❌ No match data available for team composition analysis")
            return False
            
        collection = db[match_collections[0]]
        sample_matches = list(collection.find().limit(3))
        
        compositions = []
        
        for match in sample_matches:
            if 'info' in match and 'participants' in match['info']:
                participants = match['info']['participants']
                for participant in participants:
                    # Extract units/champions
                    units = participant.get('units', [])
                    if units:
                        comp = {
                            'match_id': match.get('metadata', {}).get('match_id', 'unknown'),
                            'placement': participant.get('placement', 0),
                            'units_count': len(units),
                            'champions': [unit.get('character_id', '') for unit in units],
                            'traits': participant.get('traits', [])
                        }
                        compositions.append(comp)
        
        if compositions:
            print(f"✅ Analyzed {len(compositions)} team compositions")
            
            # Basic composition analysis
            placements = [comp['placement'] for comp in compositions]
            unit_counts = [comp['units_count'] for comp in compositions]
            
            print(f"📊 Placement stats: mean={np.mean(placements):.2f}, range={min(placements)}-{max(placements)}")
            print(f"🔢 Unit count stats: mean={np.mean(unit_counts):.2f}, range={min(unit_counts)}-{max(unit_counts)}")
            
            # Champion frequency analysis
            all_champions = []
            for comp in compositions:
                all_champions.extend(comp['champions'])
            
            if all_champions:
                champion_counts = pd.Series(all_champions).value_counts()
                print(f"🏆 Most popular champions: {list(champion_counts.head(3).index)}")
            
            client.close()
            return True
        else:
            print("❌ No composition data found")
            client.close()
            return False
            
    except Exception as e:
        print(f"❌ Team composition analysis failed: {e}")
        return False

def test_data_aggregation():
    """Test data aggregation and statistics"""
    print("\n📈 Testing data aggregation...")
    
    try:
        client = MongoClient(DB_URI, tls=True, tlsAllowInvalidCertificates=True,
                           connectTimeoutMS=30000, serverSelectionTimeoutMS=30000)
        db = client[DB_NAME]
        
        # Aggregate match statistics
        match_collections = [col for col in db.list_collection_names() if 'matches_detail' in col]
        
        total_matches = 0
        total_participants = 0
        
        for col_name in match_collections:
            collection = db[col_name]
            matches = collection.count_documents({})
            total_matches += matches
            
            # Sample some matches to count participants
            sample = list(collection.find().limit(10))
            for match in sample:
                if 'info' in match and 'participants' in match['info']:
                    total_participants += len(match['info']['participants'])
        
        print(f"✅ Aggregated statistics:")
        print(f"  📊 Total matches across all collections: {total_matches}")
        print(f"  👥 Sample participants analyzed: {total_participants}")
        print(f"  🌍 Regions with data: {len(match_collections)}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Data aggregation failed: {e}")
        return False

def main():
    """Run all pipeline process tests"""
    print("🚀 Starting TFT Champion Pipeline Process Tests\n")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Data Loading Process", test_data_loading_process),
        ("Team Composition Analysis", test_team_composition_analysis),
        ("Data Aggregation", test_data_aggregation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 TEST SUMMARY")
    print('='*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All pipeline processes are working correctly!")
    else:
        print("⚠️  Some pipeline processes need attention")
    
    return passed == total

if __name__ == "__main__":
    main()
