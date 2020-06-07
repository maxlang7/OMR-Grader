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
        jsonData = grader.grade('test/images/sat_test2.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'B', 'C', 'B', 'D', 'C', 'B'])
    
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['D', 'B', 'A', 'B', 'B', 'C', 'A'])

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['A', 'C', 'A', 'C', 'B', 'D', 'C'])

    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.png', True, True, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'][0:7], ['', '', 'B', 'A', 'C', '', ''])


if __name__ == '__main__':
    unittest.main()