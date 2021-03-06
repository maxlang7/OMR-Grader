import unittest
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
import grader as g
from wand.image import Image

class ExampleImageTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = False
    debug_mode = verbose_mode

    def test_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_page2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_Mccolloch3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/imageMc33.jpeg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        expected_answers = [ (  'D A A'.split(' ') +
                                'B B D'.split(' ') +
                                'B C A'.split(' ') +
                                'C D C'.split(' ') +
                                'B A B'.split(' ') ) ,
                             ['-', '-', 3.0, 5.0, '-']
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
        

    def test_page4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_page5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [6.0, 58.6, 9.0, 0.625, '-'],
                             [150.0, 7.0, 40.0]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    
if __name__ == '__main__':
    unittest.main()