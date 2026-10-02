#!/usr/bin/env python3
"""Unique, verified actionable selections with retained discovery history."""
import unittest
from copy import deepcopy
from scan_state import finalize_scan, ingest_candidates, start_scan
from state_store import empty_state


def candidate(slug='one', live='verified_live', disposition='worth_review'):
    return {'job':{'company':'Synthetic Co','title':'Product Manager',
                   'url':f'https://jobs.example.com/{slug}', 'text':'Synthetic role', 'live_status':live},
            'facts':{'geographies':['Germany'],'employability':'eligibility_unclear'},
            'disposition':disposition}


class ScanSelection(unittest.TestCase):
    def run_scan(self, candidates, maximum=5):
        state=empty_state(); state['search_policy']={'geographies':['Germany'],'max_results':maximum}
        scan=start_scan(state,'manual'); ingest_candidates(state,scan['id'],candidates)
        return state,finalize_scan(state,scan['id'])

    def test_deduplicate_before_applying_result_limit(self):
        first=candidate(); repost=deepcopy(first);repost['job']['url']+='?utm_source=duplicate'
        state,scan=self.run_scan([first,repost,candidate('two')],2)
        self.assertEqual(len(set(scan['selected_opportunity_ids'])),2)
        self.assertEqual(len(scan['candidates']),3)
        self.assertEqual(len(state['opportunities']),2)

    def test_unverified_and_closed_stay_in_reservoir_not_actionable_results(self):
        state,scan=self.run_scan([candidate('closed','closed'),candidate('unknown','unknown'),candidate('live')])
        self.assertEqual(len(scan['selected_opportunity_ids']),1)
        self.assertEqual(len(state['opportunities']),3)
        self.assertEqual(state['opportunities'][scan['selected_opportunity_ids'][0]]['canonical_url'],'https://jobs.example.com/live')

    def test_latest_observation_controls_eligibility_for_shortlist(self):
        first=candidate(); closed=candidate(live='closed')
        state,scan=self.run_scan([first,closed])
        self.assertEqual(scan['selected_opportunity_ids'],[])
        self.assertEqual(len(scan['candidates']),2)

    def test_verified_job_with_unknown_authorization_can_remain_verify_first(self):
        state,scan=self.run_scan([candidate(disposition='verify_first')])
        self.assertEqual(len(scan['selected_opportunity_ids']),1)
        self.assertEqual(scan['candidates'][0]['disposition'],'verify_first')
        self.assertEqual(scan['candidates'][0]['hard_constraint_check']['needs_verification'],['employability'])


if __name__ == '__main__':
    unittest.main()
