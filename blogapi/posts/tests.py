from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post

# Create your tests here.


class BlogTest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        # create a user
        testUser1 = User.objects.create_user(
            username='testUser1', password='abc123'
        )

        testUser1.save()

        # Create a blog posts
        test_post = Post.objects.create(
            author=testUser1, title='Blog Title', body="Body content..."
        )

        test_post.save()

    def test_blog_content(self):
        post = Post.objects.get(id=1)
        author = f"{post.author}"
        title = f"{post.title}"
        body = f"{post.body}"
        self.assertEqual(author, 'testUser1')
        self.assertEqual(title, 'Blog Title')
        self.assertEqual(body, 'Body content...')