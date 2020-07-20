from datetime import datetime


from zopsedu.app import scheduler
from uuid import uuid4
from zopsedu.lib.db import DB
from zopsedu.models import AppStateTracker


class BaseJobHandler(object):

    @staticmethod
    def prepare_tracker(state_id=None, job_id=None, tracker_info=None):
        if not isinstance(tracker_info, dict):
            return None

        new_tracker = AppStateTracker(
            state_id=state_id,
            params=tracker_info.get('params', None),
            date=datetime.now(),
            job_type=tracker_info.get('job_type', None),
            triggered_by=tracker_info.get("triggered_by", None),
            description=tracker_info.get("description", None),
            apscheduler_job_id=job_id
        )
        return new_tracker

    @staticmethod
    def add_jobs(jobs_info, state_id=None):
        """
        jobs_info parametresi schedular icin ihtiyac duyulan veriyi icerir list of dict bicimindedir.
        jobs_info = [
            {
                'func': JobFunc.logger_job,
                'trigger': 'cron',
                'minute': '*/5',
                'tracker_info': {
                    'params': {"project_id": 5},
                    'triggered_by': 6,
                    'description': 'SMS',
                    'job_type': JobTypes.email,
                }
            }

        ]
        :param jobs_info: list of dict
        :param state_id:
        :return:
        """
        jobs_kwargs = jobs_info
        if not isinstance(jobs_kwargs, list):
            jobs_kwargs = [jobs_kwargs]

        for job_kwargs in jobs_kwargs:
            job = None
            job_id = None
            try:
                tracker_info = job_kwargs.pop('tracker_info', None)

                job_id = uuid4().hex
                job = scheduler.scheduler.add_job(id=job_id, **job_kwargs)

                if job is not None:
                    tracker = BaseJobHandler.prepare_tracker(tracker_info=tracker_info,
                                                             job_id=job_id,
                                                             state_id=state_id)
                    DB.session.add(tracker)
                    DB.session.commit()

            except Exception as exc:
                DB.session.rollback()
                if job and job_id:
                    BaseJobHandler.remove_job([job_id])

    @staticmethod
    def pause_job(job_ids):
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.pause_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)

    @staticmethod
    def remove_job(job_ids):
        """

        :param job_ids: list of job id
        :return:
        """
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.remove_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)

    @staticmethod
    def resume_job(job_ids):
        if job_ids is not None:
            if not isinstance(job_ids, list):
                job_ids = list(job_ids)
            for job_id in job_ids:
                try:
                    scheduler.scheduler.resume_job(job_id=job_id)
                except Exception as exc:
                    raise Exception(exc)
