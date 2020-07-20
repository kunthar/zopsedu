import copy
from datetime import datetime

from zopsedu.app import job_store, scheduler
from uuid import uuid4
from zopsedu.lib.db import DB
from zopsedu.models import AppStateTracker


class JobHandler:
    def __init__(self, remove_jobs=None ,pause_jobs=None ,add_jobs=None, resume_jobs=None):
        self.job_store = job_store
        self.remove_jobs = remove_jobs
        self.pause_jobs = pause_jobs
        self.add_jobs = add_jobs
        self.resume_jobs = resume_jobs

    def prepare_tracker(self, state_id=None, job_id=None, tracker_info=None):
        try:
            new_tracker = AppStateTracker(
                state_id=state_id,
                params=tracker_info['params'],
                date=datetime.now(),
                job_type=tracker_info['job_type'],
                triggered_by=tracker_info['triggered_by'],
                description=tracker_info['description'],
                apscheduler_job_id=job_id
                )
            return new_tracker
        except Exception as exc:
            raise Exception(exc)

    @staticmethod
    def start_job(job_kwargs=None):
        try:
            id = uuid4().hex
            job = scheduler.scheduler.add_job(id=id, **job_kwargs)
        except Exception as exc:
            raise Exception(exc)

        return job

    def add_job(self, state_id=None):
        jobs_kwargs = self.jobs

        if jobs_kwargs is not None:
            if not isinstance(jobs_kwargs, list):
                jobs_kwargs = [jobs_kwargs]

            for job_kwargs in jobs_kwargs:
                try:
                    job_info = copy.deepcopy(job_kwargs)
                    tracker_info = job_info.pop('tracker_info')
                    job = self.start_job(job_kwargs=job_info)
                    if job is not None:
                        tracker = self.prepare_tracker(tracker_info=tracker_info, job_id=job.id,
                                                       state_id=state_id)
                        DB.session.add(tracker)
                        DB.session.commit()

                except Exception as exc:
                    raise Exception(exc)

    def pause_job(self):
        job_ids = self.pause_jobs
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.pause_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)

    def remove_job(self):
        job_ids = self.remove_jobs
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.remove_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)

    def resume_job(self):
        job_ids = self.resume_jobs
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.resume_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)
