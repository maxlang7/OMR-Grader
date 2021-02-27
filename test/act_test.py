import unittest
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
import grader as g
from wand.image import Image

class ExampleActTests(unittest.TestCase):
    #turn both to true to see images.
    verbose_mode = False
    debug_mode = verbose_mode

    def test_act_page1(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1.JPG', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)

        expected_answers = [ ('A J D H B J B J C J B G A ' +
                              'H D H B H C H A F B H C F ' +
                              'D G A F B H B H A F A F C ' +
                              'J C G D J C J D H B F D J ' +
                              'A F D G C F D G C H A F C ' +
                              'H D G D J A F B H D').split(' '),
                            
                             ('D H E F E H E H A K ' +
                              'C K B H B H D F D F ' +
                              'B H A H B G A H C G ' +
                              'E K B H D J A F B F ' +
                              'E K D G D J B G A F ' +
                              'E H B K E K A K E J').split(' '),
                            
                             ('A J C H B J A ' +
                              'H B J A H C J ' +
                              'B H B F D F A ' +
                              'G D J C G C J ' +
                              'C G A G A J D ' +
                              'H B J A H').split(' '),
                            
                             ('C G D G C F A ' +
                              'F D J C F B F ' +
                              'C F B H B J D ' +
                              'F B J B H A J ' +
                              'C F B G D J A ' +
                              'H B F D J').split(' ')
                            ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_act_page1a(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1a.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)
        
        expected_answers = [ ('A J D H B J B F D J B G A ' +
                              'H D H D F A H A F B H A G ' +
                              'D F A F B G D H A F A F C ' +
                              'J B G C J D J C H B G D F ' +
                              'A F B G C F A G B G A F C ' +
                              'F D G B H D F - - -').split(' '),
                            
                             ('D H D F E H E H A K ' +
                              'C K B H D H A F D F ' +
                              'B H A H B G E H - H ' +
                              'D K B G C G A F B F ' +
                              'D J D G D G B F D G ' +
                              'E J B H D K C G B H').split(' '),
                            
                             ('A J B H B H A ' +
                              'H B J B J C J ' +
                              'B F B H D F A ' +
                              'G C J B J C J ' +
                              'C G A H B H A ' +
                              '- - - - -').split(' '),
                            
                             ('C G D G B F A ' +
                              'F D H C J B F ' +
                              'C K A H B J D ' +
                              'F B J B H A G ' +
                              'C F B G D G B ' +
                              'G C H B H').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                   
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
            
    def test_act_page1b(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1b.png', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
        data = json.loads(jsonData)
        expected_answers = [ ('A J D H B J B J C J B G A ' +
                              'H D H D H C G A F B H D F ' +
                              'D J A J D G B H A F A F C ' +
                              'J C G C F C J C H B G B J ' +
                              'D F D F C F B H C H A F C ' +
                              'H C H C H C H C H C').split(' '),
                            
                             ('D H E F E H E H A K ' +
                              'C K C G B H D F D F ' +
                              'B F A H B G E H C F ' +
                              'D K B H E H A F B F ' +
                              'D K D G E J B G D F ' +
                              'E H D K E H D J E G').split(' '),
                            
                             ('D J C H B J A ' +
                              'H B J A J C F ' +
                              'B H B F D F B ' +
                              'H D H C F C J ' +
                              'A H A G A J A ' +
                              'J B G B F').split(' '),
                            
                             ('C G D G C F C ' +
                              'F D J C H C F ' +
                              'C F B H A J D ' +
                              'F B G A G A J ' +
                              'D F B G D J A ' +
                              'H C G A J').split(' ')
                          ]
        self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
        self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")                   
        for i, graded_results in enumerate(data['boxes']):
            print(f'ACT test {i+1}')
            self.assertEqual(len(graded_results['results']['bubbled']),len(expected_answers[i]))        
            self.assertEqual(list(graded_results['results']['bubbled'].values()), expected_answers[i])
    
    def test_act_page1c(self):
        grader = g.Grader()
        jsonData = grader.grade('test/images/act_test1c.png', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
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
            
    def test_act_simple(self):
        answer_counts = [75, 60, 40, 40]
        for testsuffix in ['d', 'f', 'g', 'h']:
            print(f'act test 1{testsuffix}')
            grader = g.Grader()
            jsonData = grader.grade(f'test/images/act_test1{testsuffix}.jpg', self.debug_mode, self.verbose_mode, 1.0, 'act', 1)
            data = json.loads(jsonData)

            self.assertIn('boxes', data, f"We couldn't find any boxes because we enountered this error: {data['error']}")
            self.assertGreater(len(data['boxes']), 0, f"We couldn't find any boxes because we enountered this error: {data['error']}")

            for i, graded_results in enumerate(data['boxes']):
                print(f'ACT test 1{testsuffix} box {i+1}')
                self.assertEqual(len(graded_results['results']['bubbled']),answer_counts[i], len(graded_results['results']['bubbled']))  
                blank_answers_num = len([a for a in graded_results['results']['bubbled'] if a == '-'])
                self.assertEqual(blank_answers_num, 0)
if __name__ == '__main__':
    unittest.main()