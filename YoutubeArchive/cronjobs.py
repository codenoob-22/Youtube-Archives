CRONJOBS = (
    ('*/5 * * * *', 'video_store.tasks.fetch_and_add_videos_to_db'),
    ('*/5 * * * *', 'video_store.tasks.complete_remaining_jobs'),
    ('*/5 * * * *', 'video_store.tasks.refresh_keys')
)