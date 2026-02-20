from utils.logger import log


class FinalSummaryEngine:
    def __init__(self, cfg_mgr):
        self.cfg_mgr = cfg_mgr
        self.on_final_summary = None  # callback

    async def run(self, live_data):
        log.info("FinalSummaryEngine generating final summary.")
        if self.on_final_summary:
            await self.on_final_summary(live_data)
