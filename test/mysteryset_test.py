import unittest
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
import grader as g

class ExampleImageTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = False
    debug_mode = verbose_mode

    def test_Gan1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_Gan2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_Gan3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
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
        

    def test_Gan4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_Gan5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan6.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [102.0, 2.0, 30.0, 25.4, 2.0],
                             [7.0, 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_ek1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/ek1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_ek2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/ek2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_ek3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/ek3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
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
        

    def test_ek4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/ek4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_ek5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/ek5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [102.0, 2.0, 30.0, 25.4, 2.0],
                             [7.0, 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_mot1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/mot1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_mot2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/mot2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_mot3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/mot3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
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
        

    def test_mot4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/mot4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_mot5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/mot5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [102.0, 2.0, 30.0, 25.4, 2.0],
                             [7.0, 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_jaj1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/jaj1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_jaj2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/jaj2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_jaj3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/jaj3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
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
        

    def test_jaj4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/jaj4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_jaj5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/jaj5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [102.0, 2.0, 30.0, 25.4, 2.0],
                             [7.0, 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_kal1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/kal1.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 1)
        data = json.loads(jsonData)
        self.assertIsNotNone(data['boxes'])
        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),52)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'B C A A C A A B B D D D C'.split(' ') +
                                                                    'B B C B B A A D A A B C C'.split(' ') +
                                                                    'B B D D B C C D C A D C A'.split(' ') +
                                                                    'D A C C D D C B B A B D D'.split(' ') )

    def test_kal2(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/kal2.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 2)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),44)        
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()),'A B C C A B A D C'.split(' ') +
                                                    'C B A C D B C C B'.split(' ') +
                                                    'D C D A A D B A D'.split(' ') +
                                                    'B A A D B C C B C'.split(' ') +
                                                    'B C C B D A D D'.split(' ') )  
    
    def test_kal3(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/kal3.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 3)
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
        

    def test_kal4(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/kal4.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 4)
        data = json.loads(jsonData)

        self.assertEqual(len(list(data['boxes'][0]['results']['bubbled'].values())),30 )
        self.assertEqual(list(data['boxes'][0]['results']['bubbled'].values()), 'C B C C B A'.split(' ') +
                                                    'D C B D B D'.split(' ') +
                                                    'D A A B B B'.split(' ') +
                                                    'C B C - C -'.split(' ') +
                                                    'D C C D A A'.split(' ') )
    
                                             
    
    
    def test_kal5(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/kal5.jpg', self.debug_mode, self.verbose_mode, 1.0, 'sat', 5)
        data = json.loads(jsonData)
        
        expected_answers = [ [102.0, 2.0, 30.0, 25.4, 2.0],
                             [7.0, 576.0, 0.8]
                           ]

        for i, graded_results in enumerate(data['boxes']):
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_Gan_act(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Gan0.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        expected_answers = [ ('A J D H B J B J C J B G A ' +
                              'H D H B J C H C F B H A F ' +
                              'D G A F B H B H A F A F C ' +
                              'J C G D J C J D H B F D J ' +
                              'A F B G C F D G C G A F C ' +
                              'H D G D J A F B H D').split(' '),
                            
                             ('D H E F E H E H A K ' +
                              'C K B H B H D F D F ' +
                              'B H A H B G E H C G ' +
                              'C K B H D J A H B F ' +
                              'E K D G D J B G A F ' +
                              'D H B K E J A K C J').split(' '),
                            
                             ('A J C H B J A ' +
                              'H B J A J B J ' +
                              'B H B F D F A ' +
                              'G D J C H C J ' +
                              'C G A G A J D ' +
                              'H B J A H').split(' '),
                            
                             ('C G D G C F A ' +
                              'F D J C F B F ' +
                              'C F B H B H D ' +
                              'F B J B H A J ' +
                              'C F B G D H A ' +
                              'H B H D J').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                  
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_Fle(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/fle.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        expected_answers = [ ('A J D H B J B J C J B G A ' +
                              'H D H B J C H C F B H A F ' +
                              'D G A F B H B H A F A F C ' +
                              'J C G D J C J D H B F D J ' +
                              'A F B G C F D G C G A F C ' +
                              'H D G D J A F B H D').split(' '),
                            
                             ('D H E F E H E H A K ' +
                              'C K B H B H D F D F ' +
                              'B H A H B G E H C G ' +
                              'C K B H D J A H B F ' +
                              'E K D G D J B G A F ' +
                              'D H B K E J A K C J').split(' '),
                            
                             ('A J C H B J A ' +
                              'H B J A J B J ' +
                              'B H B F D F A ' +
                              'G D J C H C J ' +
                              'C G A G A J D ' +
                              'H B J A H').split(' '),
                            
                             ('C G D G C F A ' +
                              'F D J C F B F ' +
                              'C F B H B H D ' +
                              'F B J B H A J ' +
                              'C F B G D H A ' +
                              'H B H D J').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                  
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])   
    
    def test_Dep(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Dep.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        expected_answers = [ ('A H D J C J B J D J B G F ' +
                              'H D G B H C H A F B H C F ' +
                              'D G A F B G B H A F D F C ' +
                              'J C G D J C J B H B F B J ' +
                              'A F B G C F D G C F C H C ' +
                              'H C H C H C H C H C').split(' '),
                            
                             ('D H D F E H E H A K ' +
                              'C K B H B H D F D F ' +
                              'B H A J B G E H C G ' +
                              'D K E H D G A F B F ' +
                              'E K D G D J F G D F ' +
                              'E K D G E G B H E G').split(' '),
                            
                             ('A G B H B F A ' +
                              'H B H A J D H ' +
                              'C G B J B F - ' +
                              '- B H C H C H ' +
                              'C H C H C H C ' +
                              'H B H C H').split(' '),
                            
                             ('C G D G C F A ' +
                              'F D J C F B J ' +
                              'C F B J B G D ' +
                              'J C G F H A G ' +
                              'C F B G D H B ' +
                              'H A H A H').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                  
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])

    def test_Wes(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/mystery_tests/Wes.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        expected_answers = [ ('D J D H D J B J B G B J B ' +
                              'H D H B F B H A F B J B F ' +
                              'D H A G D G B G A F A F C ' +
                              'J C G D J C F C H A F D J ' +
                              'A F B G C F D G C H D H D ' +
                              'H A G B J A G B F D').split(' '),
                            
                             ('D H E F E H C H A K ' +
                              'A K B H A G D F A F ' +
                              'B H A H B G B F D G ' +
                              'D H B J D J A J B F ' +
                              'C J E G C F E H B J ' +
                              'E G B F D J C J B K').split(' '),
                            
                             ('A J C H B F D ' +
                              'H B H A J C J ' +
                              'B H B F D F A ' +
                              'G D J B G A J ' +
                              'A H A G A F C ' +
                              'F A G B H').split(' '),
                            
                             ('C G D G C F A ' +
                              'F D F B J D J ' +
                              'C J B H B J C ' +
                              'F B J B G A G ' +
                              'B F A G D F A ' +
                              'F B F A F').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                  
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])


if __name__ == '__main__':
    unittest.main()