from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError



from .models import Video

class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Exercise Videos')

class TestAddVideos(TestCase):
    # Adding a video, added to DB and video_id created 

    def test_add_video(self):

        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'yoga',
            'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
            'notes': 'yoga for neck and shoulders'
        }

        url = reverse('add_video')
        response = self.client.post(url, data=valid_video, follow=True)

        # redirect to video list 
        self.assertTemplateUsed('video_collection/video_list.html')

        #does the video list show the new video!
        self.assertContains(response, 'yoga')
        self.assertContains(response, 'https://www.youtube.com/watch?v=4vTJHUDB5ak')
        self.assertContains(response, 'yoga for neck and shoulders')

        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first() 

        self.assertEqual('yoga', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=4vTJHUDB5ak', video.url)
        self.assertEqual('yoga for neck and shoulders', video.notes)
        self.assertEqual('4vTJHUDB5ak', video.video_id)


    def test_add_video_missing_fields(self):

        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'name': '',   # no name, should not be allowed 
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=4vTJHUDB5ak',
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',   
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': 'example',  
                # no URL 
                'notes': 'yoga for neck and shoulders'
            },
            {
                # no name
                # no URL
                'notes': 'yoga for neck and shoulders'
            },
            {
                'name': '',   # blank - not allowed 
                'url': '',   # no URL, should not be allowed 
                'notes': 'yoga for neck and shoulders'
            },

        ]

        
        for invalid_video in invalid_videos:

            # follow=True not necessary because if video not valid, will expect a simple response
            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed('video_collection/add_video.html')  # still on add page 
            self.assertEqual(0, Video.objects.count())  # no video added to database 
            messages = response.context['messages']    # get the messages
            message_texts = [ message.message for message in messages ]   # and the message texts
            self.assertIn('Please check the data entered.', message_texts)   # is this message one of the messages?
            

            # And we can also check that message is displayed on the page 
            self.assertContains(response, 'Please check the data entered.')
           







class TestVideoList(TestCase):
     # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No Videos')
        self.assertEqual(0, len(videos_in_template))

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos') 

    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')       
       
    

class TestVideoSearch(TestCase):
    def test_all_videos_displayed_in_correct_order(self):

        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v2, v4, v3, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    # No video message 

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No videos')
        self.assertEquals(0, len(videos_in_template))


    # 1 video vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')   # check this, because '1 videos' contains '1 video'


    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)


    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')
        
        expected_video_order = []  # empty list 
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')

    

class TestVideoModel(TestCase):

    def duplicate_video_raises_integrity_error(self):
        v1 = Video.objects.create(name='ZXY', url='https://www.youtube.com/watch?v=IODxDxX7oi4', notes= 'example')
        with self.assertRaises(IntegrityError):
           Video.objects.create(name='ZXY', url='https://www.youtube.com/watch?v=IODxDxX7oi4', notes= 'example')
    

    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=xv1Igh6',
            'https://www.youtube.com/watch?v1234',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456'
            
        ]

        for invalid_video_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_video_url , notes='example notes')

        
        self.assertEqual(0, Video.objects.count())



    
    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)


    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example', url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        self.assertCountEqual(expected_videos, database_videos)  # check contents of two lists/iterables but order doesn't matter.    