import unittest
import json
import grader as g

class ExampleImageTests(unittest.TestCase):

    def test_6q(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1.png', True, True, 1.0, 'act', 1)
        data = json.loads(jsonData)

        self.assertEqual(data['answer']['bubbled'], ['A', 'B', 'B', 'C', 'C', 'D'])
if __name__ == '__main__':
    unittest.main()