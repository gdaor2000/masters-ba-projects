import sys
sys.path.append("./Functions")
from real_distances import calculate_distance_between_airports
import pytest

def test_distance_between_same_airport():
    # Test when source and destination airports are the same
    distance = calculate_distance_between_airports('JFK', 'JFK')
    assert distance == 0   #answer:0    
    
def test_distance_between_close_airports():
    # Test when source and destination airports are close to each other
    distance = calculate_distance_between_airports('JFK', 'LGA')
    assert distance == pytest.approx(17, rel=0.05)    #answer: 17

def test_distance_between_distant_airports():
    # Test when source and destination airports are distant from each other
    distance = calculate_distance_between_airports('JFK', 'MAG')
    assert distance == pytest.approx(14400, rel=0.05)  #answer: 14445
