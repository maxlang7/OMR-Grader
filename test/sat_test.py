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

    def test_FAIL(self):
        grader = g.Grader()
        jsonData = grader.grade(f'test/images/failtest1.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data)
        self.assertEqual(data['status'], 2)
    
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
    
    def test_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'D B A A D A D B B D D D A'.split(' ') +
                                                                   'D D A C C A B C B B B C B'.split(' ') +
                                                                   'D D B B C B B A C A B C A'.split(' ') +
                                                                   'A B D D B A B C A C B D A'.split(' ') )

    def test_page1c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1c.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C C D D C D B C B D D D'.split(' ') +
                                                                    'A D B C B D A C A D A B C'.split(' ') +
                                                                    'B C D C D B C B C B C D D'.split(' ') +
                                                                    'A D A C A C A C B B B C C'.split(' ') )
    
    def test_jpgtest(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1a.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'D B A A D A D B B D D D A'.split(' ') +
                                                                   'D D A C C A B C B B B C B'.split(' ') +
                                                                   'D D B B C B B A C A B C A'.split(' ') +
                                                                   'A B D D B A B C A C B D A'.split(' ') )


    def test_heictest(self):
        grader = g.Grader()
        with Image(filename='test/images/sat_test1a.heic') as img:  
            img.format = 'jpeg'
            img.save(filename='test/images/sat_test1a.heic_jpeg')
        jsonData = grader.grade('test/images/sat_test1a.heic_jpeg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'D B A A D A D B B D D D A'.split(' ') +
                                                                   'D D A C C A B C B B B C B'.split(' ') +
                                                                   'D D B B C B B A C A B C A'.split(' ') +
                                                                   'A B D D B A B C A C B D A'.split(' ') )

    def test_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test1b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)

        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values())[0:7], ['A', 'C', 'D', 'D', 'A', 'D', 'D'])
    
    def test_page2a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B B A A D D B D B'.split(' ') +
                                                    'B B B D C C C B B'.split(' ') +
                                                    'A D D B A B B D D'.split(' ') +
                                                    'A C C B B B D A A'.split(' ') +
                                                    'D B C D D B A C'.split(' ') )

    def test_page2b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'D B C B D C B C A'.split(' ') +
                                                    'D A A D C A D C B'.split(' ') +
                                                    'D A B D C C C A C'.split(' ') +
                                                    'B B B B D B B D B'.split(' ') +
                                                    'B D C D B C D D'.split(' ') )
    def test_page2c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test2c.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'D B C B D C B A A'.split(' ') +
                                                    'C A A D C C A D B'.split(' ') +
                                                    'A B B D D C C A C'.split(' ') +
                                                    'B B B B D D D D B'.split(' ') +
                                                    'B D C A A D B B'.split(' ') )                                            
    def test_page3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        expected_answers = [ (  'C D D'.split(' ') +
                                'B C C'.split(' ') +
                                'C A -'.split(' ') +
                                'A C -'.split(' ') +
                                '- A D'.split(' ') ) ,
                             ['-', '-', '-', 320.0, '-']
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_page3a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        expected_answers = [ (  'C B A'.split(' ') +
                                'A C C'.split(' ') +
                                'A D B'.split(' ') +
                                'C C B'.split(' ') +
                                'D A D'.split(' ') ) ,
                             [3.0, 19.0, 12.0, 6.0, 0.25]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])                                               
   
    def test_page3b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        expected_answers = [ (  'D B A'.split(' ') +
                                'B B B'.split(' ') +
                                'C D A'.split(' ') +
                                'B B D'.split(' ') +
                                'C D B'.split(' ') ),
                             [3.0, 32.0, 1.5, 8.0, 144]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_page3c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test3c.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
        data = json.loads(jsonData)

        expected_answers = [ (  'D A A'.split(' ') +
                                'C B C'.split(' ') +
                                'B D A'.split(' ') +
                                'C B D'.split(' ') +
                                'C C B'.split(' ') ),
                             [3.0, 32.0, 1.5, 8.0, 144.0]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_page4a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B A C C B'.split(' ') +
                                                    'D D A B B D'.split(' ') +
                                                    'B C A B C C'.split(' ') +
                                                    'B C D B C A'.split(' ') +
                                                    'B D C B A B'.split(' ') )

    def test_page4b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'A C A C B D'.split(' ') +
                                                    'C A A A D C'.split(' ') +
                                                    'A D D B A C'.split(' ') +
                                                    'A A D A B D'.split(' ') +
                                                    'B A D A D B'.split(' ') )
    def test_page4c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test4c.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30)
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'A C A C B D'.split(' ') +
                                                    'A B C A B C'.split(' ') +
                                                    'D C C B A C'.split(' ') +
                                                    'C B D D B D'.split(' ') +
                                                    'B C B D C C'.split(' ') )
    
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
    
    def test_page5a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5a.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [14.0, 7.0, 11.0, 105.0, 15.0],
                             [32.0, 3284.0, 7500.0]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_page5b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5b.png', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        expected_answers = [ [102.0, 2.0, 60.0, 25.4, '-'],
                             ['-', 34.0, '-']
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_page5c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/sat_test5c.JPG', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)

        expected_answers = [ [34.0, 2.0, 30.0, 4.77, 2.0],
                             ['-', 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

if __name__ == '__main__':
    unittest.main()