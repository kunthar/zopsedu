class AppStateManager:

    def change_state(self, dispacther=None, job_handler=None):
        try:
            state_id = dispacther.state_change()
            job_handler.add_job(state_id=state_id)
            job_handler.remove_job()

        except Exception as exc:
            raise Exception(exc)
