from django.db import models


# Create your models here.
class EmailLog(models.Model):
    """
    邮件日志
    """
    recipients = models.CharField(verbose_name="收件人", max_length=300)
    subject = models.CharField(verbose_name="主题", max_length=2000)
    message = models.TextField(verbose_name="内容")
    send_result = models.BooleanField(verbose_name="发送结果", default=False)
    created_time = models.DateTimeField(verbose_name="发送时间", auto_now_add=True)

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "邮件发送日志"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
