import unittest
import json
import grader as g

class ExampleImageTests(unittest.TestCase):

    def test_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['D', 'C', 'C', 'D', 'C', 'C', 'D'])

    def test_page2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2.png', True, True, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'B', 'C', 'B', 'D', 'C', 'B'])
    
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.png', True, True, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:8], ['D', 'B', 'A', 'B', 'B', 'C', 'A', 'C'])

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.png', True, True, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'C', 'A', 'C', 'B', 'D', 'C'])

    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.png', True, True, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(data['answer']['bubbled'], ['D', 'B', 'A', 'A', 'D', 'A', 'D', 'B', 'B', 'D', 'D', 'D', 'A', 'D', 'D', 'A', 'C', 'C', 'A', 'B', 'C', 'B', 'B', 'B', 'C', 'B', 'D', 'D', 'B', 'B', 'C', 'B', 'B', 'A', 'C', 'A', 'B', 'C', 'A', 'A', 'B', 'D', 'D', 'B', 'A', 'B', 'C', 'A', 'C', 'B', 'D', 'A'])
        
    def test_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1b.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        print(data['answer']['bubbled'])

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2a.png', True, True, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])

    def test_page2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2b.png', True, True, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page3a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', True, True, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page3b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3b.png', True, True, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])

    def test_page4a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4a.png', True, True, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])

    def test_page4b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4b.png', True, True, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page5a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', True, True, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
    
    def test_page5b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', True, True, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])
if __name__ == '__main__':
    unittest.main()