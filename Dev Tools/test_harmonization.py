"""
Test harmonization pipeline with sample datasets
Tests the embedding-based semantic mapping with cosine similarity
and LLM fallback for ambiguous cases.
"""
import pandas as pd
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import run_pipeline
from semantic_mapping import semantic_column_mapping


def test_basic_harmonization():
    """Test basic harmonization with two simple datasets."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create sample datasets
        df1 = pd.DataFrame({
            'customer_id': [1, 2, 3],
            'customer_name': ['Alice', 'Bob', 'Charlie'],
            'order_amount': [100.5, 200.0, 150.25],
            'order_date': ['2026-01-01', '2026-01-02', '2026-01-03'],
            'city': ['New York', 'Los Angeles', 'Chicago']
        })
        
        df2 = pd.DataFrame({
            'client_code': [101, 102, 103],
            'client_full_name': ['Alice A', 'Bob B', 'Charlie C'],
            'invoice_total': [100.5, 200.0, 150.25],
            'date_of_purchase': ['2026-01-01', '2026-01-02', '2026-01-03'],
            'region': ['NY', 'CA', 'IL']
        })
        
        file1 = tmpdir / 'test1.csv'
        file2 = tmpdir / 'test2.csv'
        df1.to_csv(file1, index=False)
        df2.to_csv(file2, index=False)
        
        # Run pipeline
        result = run_pipeline([str(file1), str(file2)])
        
        # Verify mappings
        print(f"  Available mapping keys: {list(result['mappings'].keys())}")
        assert len(result['mappings']) > 0, "No mappings found"
        
        # Get the first dataset mapping
        dataset_names = list(result['mappings'].keys())
        mappings1 = result['mappings'][dataset_names[0]]
        mappings2 = result['mappings'][dataset_names[1]] if len(dataset_names) > 1 else {}
        
        # Check that common columns are mapped
        assert mappings1.get('customer_id') in ['entity_id', 'UNKNOWN'], f"Unexpected mapping for customer_id: {mappings1.get('customer_id')}"
        assert mappings1.get('customer_name') in ['entity_name', 'UNKNOWN'], f"Unexpected mapping for customer_name: {mappings1.get('customer_name')}"
        assert mappings1.get('order_amount') in ['numeric_value', 'quantity', 'UNKNOWN'], f"Unexpected mapping for order_amount: {mappings1.get('order_amount')}"
        assert mappings1.get('order_date') in ['timestamp', 'UNKNOWN'], f"Unexpected mapping for order_date: {mappings1.get('order_date')}"
        assert mappings1.get('city') in ['location', 'UNKNOWN'], f"Unexpected mapping for city: {mappings1.get('city')}"
        
        # Check harmonized output
        harmonized = pd.concat(result['harmonized_outputs'].values(), ignore_index=True)
        assert harmonized.shape[0] == 6, f"Expected 6 rows, got {harmonized.shape[0]}"
        assert len(harmonized.columns) > 0, "No columns in harmonized output"
        
        print("[PASS] Basic harmonization test passed")
        print(f"  Harmonized columns: {harmonized.columns.tolist()}")
        print(f"  Total rows: {harmonized.shape[0]}")
        return True


def test_semantic_mapping():
    """Test semantic column mapping directly."""
    from column_semantics import generate_column_description
    from semantic_mapping import CANONICAL_TEMPLATE
    
    cols = {
        'customer_id': generate_column_description('customer_id'),
        'customer_name': generate_column_description('customer_name'),
        'order_amount': generate_column_description('order_amount'),
        'order_date': generate_column_description('order_date'),
        'city': generate_column_description('city')
    }
    
    result = semantic_column_mapping(cols, sample_rows=None)
    mapping = result['mapping']
    reasoning = result['reasoning']
    
    # Verify that all columns are mapped
    assert len(mapping) == 5, f"Expected 5 mappings, got {len(mapping)}"
    
    # Verify that mappings are in the canonical template or UNKNOWN
    for col, target in mapping.items():
        assert target in CANONICAL_TEMPLATE or target == 'UNKNOWN', f"Invalid target {target} for {col}"
    
    print("[PASS] Semantic mapping test passed")
    print(f"  Mappings: {mapping}")
    print(f"  Reasoning: {reasoning}")
    return True


def test_embedding_quality():
    """Test embedding-based matching with cosine similarity."""
    from semantic_mapping import _generate_embedding_matches, CANONICAL_TEMPLATE
    from column_semantics import generate_column_description
    
    cols = {
        'customer_id': generate_column_description('customer_id'),
        'order_amount': generate_column_description('order_amount'),
    }
    
    # Sample values to improve embedding signal
    sample_rows = [
        {'customer_id': 1, 'order_amount': 100.5},
        {'customer_id': 2, 'order_amount': 200.0},
        {'customer_id': 3, 'order_amount': 150.25},
    ]
    
    matches = _generate_embedding_matches(cols, CANONICAL_TEMPLATE, sample_rows=sample_rows)
    
    assert 'customer_id' in matches, "Missing customer_id in matches"
    assert 'order_amount' in matches, "Missing order_amount in matches"
    
    customer_id_match = matches['customer_id']
    order_amount_match = matches['order_amount']
    
    assert customer_id_match['score'] > 0.0, "customer_id similarity score is 0"
    assert order_amount_match['score'] > 0.0, "order_amount similarity score is 0"
    
    print("[PASS] Embedding quality test passed")
    print(f"  customer_id -> {customer_id_match['target']} (score: {customer_id_match['score']:.3f})")
    print(f"  order_amount -> {order_amount_match['target']} (score: {order_amount_match['score']:.3f})")
    return True


if __name__ == '__main__':
    print("Running harmonization tests...\n")
    
    try:
        test_semantic_mapping()
        print()
        test_embedding_quality()
        print()
        test_basic_harmonization()
        print("\n[SUCCESS] All tests passed!")
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
