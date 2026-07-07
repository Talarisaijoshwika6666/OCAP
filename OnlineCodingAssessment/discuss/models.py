from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Post(models.Model):
    TAG_CHOICES = [
        ('Question', 'Question'),
        ('Solution', 'Solution'),
        ('Debug Help', 'Debug Help'),
        ('Interviews', 'Interviews'),
        ('General', 'General'),
    ]
    title = models.CharField(max_length=300)
    body = models.TextField()
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='General')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return self.title

    def like_count(self):
        return self.likes.count()

class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_replies', blank=True)

    def __str__(self):
        return f"Reply by {self.author} on {self.post}"