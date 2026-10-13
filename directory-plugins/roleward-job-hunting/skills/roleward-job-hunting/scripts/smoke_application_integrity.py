#!/usr/bin/env python3
"""Application history, changed-source review, and saved-artifact regressions."""
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from application_state import record_artifact, record_positioning_draft, review_positioning
from context_state import AUTH_CONFIRMED, add_career_evidence
from opportunity_state import record_assessment, upsert_opportunity
from state_store import empty_state, load_state, save_state

ROOT = Path(__file__).resolve().parents[1]


class ApplicationIntegrity(unittest.TestCase):
    def setUp(self):
        self.state = empty_state()
        self.evidence = add_career_evidence(self.state, domain='experience',
            statement='Owned a synthetic B2B workflow', authority=AUTH_CONFIRMED, source_ids=[])
        self.job = {'company':'Synthetic Co', 'title':'Product Manager',
            'url':'https://jobs.example.com/pm', 'text':'Own a B2B workflow.'}
        self.opp_id, _ = upsert_opportunity(self.state, self.job)
        self.content = {'thesis':'B2B workflow ownership', 'proof_points':[self.evidence]}
        self.draft = record_positioning_draft(self.state, self.opp_id, self.content)

    def payload(self):
        return {'claims':[{'text':'Owned a synthetic B2B workflow', 'evidence_ids':[self.evidence]}]}

    def test_caller_edits_cannot_rewrite_draft(self):
        frozen = deepcopy(self.draft)
        self.content['proof_points'].append('invented')
        self.assertEqual(self.draft, frozen)

    def test_review_and_parent_do_not_share_mutable_content(self):
        reviewed = review_positioning(self.state, self.opp_id, self.draft['id'])
        frozen = deepcopy(reviewed)
        self.draft['content']['proof_points'].append('later caller mutation')
        self.assertEqual(reviewed, frozen)

    def test_edited_review_and_artifact_metadata_are_snapshots(self):
        edited = {'thesis':'Edited positioning', 'proof_points':[self.evidence]}
        reviewed = review_positioning(self.state, self.opp_id, self.draft['id'], edited_content=edited)
        frozen = deepcopy(reviewed)
        edited['proof_points'].clear()
        self.assertEqual(reviewed, frozen)
        payload = {'contacts':[{'name':'Synthetic Example'}], 'metadata':{'notes':['synthetic control']}}
        artifact = record_artifact(self.state, self.opp_id, 'contact_shortlist', payload)
        frozen_artifact = deepcopy(artifact)
        payload['contacts'][0]['name'] = 'changed'
        payload['metadata']['notes'].clear()
        self.assertEqual(artifact, frozen_artifact)

    def test_changed_job_rejects_old_review_without_mutation_then_recovers(self):
        reviewed = review_positioning(self.state, self.opp_id, self.draft['id'])
        artifact = record_artifact(self.state, self.opp_id, 'resume', self.payload())
        frozen_artifact = deepcopy(artifact)
        upsert_opportunity(self.state, {**self.job, 'text':'Own a different enterprise platform.'})
        before = deepcopy(self.state)
        with self.assertRaisesRegex(ValueError, 'current job source'):
            record_artifact(self.state, self.opp_id, 'resume', self.payload())
        self.assertEqual(self.state, before)
        with self.assertRaisesRegex(ValueError, 'current job source'):
            review_positioning(self.state, self.opp_id, self.draft['id'])
        self.assertEqual(self.state, before)
        fresh = record_positioning_draft(self.state, self.opp_id, self.content)
        new_review = review_positioning(self.state, self.opp_id, fresh['id'])
        new_artifact = record_artifact(self.state, self.opp_id, 'resume', self.payload())
        self.assertEqual(artifact, frozen_artifact)
        self.assertNotEqual(new_artifact['source_snapshot_id'], artifact['source_snapshot_id'])
        self.assertEqual(new_artifact['positioning_revision_id'], new_review['id'])
        self.assertEqual(artifact['positioning_revision_id'], reviewed['id'])

    def test_new_job_draft_does_not_inherit_old_assessment_provenance(self):
        payload = json.loads((ROOT / 'fixtures/_inputs/direct-opportunity-assessment.json').read_text())
        payload['job'] = dict(self.job)
        original = record_assessment(self.state, payload)['assessment']
        matching = record_positioning_draft(self.state, self.opp_id, self.content)
        self.assertEqual(matching['pursuit_assessment_id'], original['id'])
        changed_job = {**self.job, 'text':'Own a different enterprise platform.'}
        upsert_opportunity(self.state, changed_job)
        fresh = record_positioning_draft(self.state, self.opp_id, self.content)
        self.assertIsNone(fresh['pursuit_assessment_id'])
        payload['job'] = changed_job
        updated = record_assessment(self.state, payload)['assessment']
        current = record_positioning_draft(self.state, self.opp_id, self.content)
        self.assertEqual(current['pursuit_assessment_id'], updated['id'])
        self.assertEqual(matching['pursuit_assessment_id'], original['id'])

    def test_unchanged_job_reobservation_keeps_review_usable(self):
        reviewed = review_positioning(self.state, self.opp_id, self.draft['id'])
        upsert_opportunity(self.state, dict(self.job))
        artifact = record_artifact(self.state, self.opp_id, 'resume', self.payload())
        self.assertEqual(artifact['positioning_revision_id'], reviewed['id'])

    def test_supplied_file_must_exist_before_recording_and_reload_keeps_hash(self):
        review_positioning(self.state, self.opp_id, self.draft['id'])
        work = ROOT / 'work'; work.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as td:
            missing = Path(td)/'resume.txt'
            before = deepcopy(self.state)
            with self.assertRaisesRegex(ValueError, 'existing file'):
                record_artifact(self.state, self.opp_id, 'resume', {**self.payload(), 'local_path':str(missing)})
            self.assertEqual(self.state, before)
            missing.write_text('Owned a synthetic B2B workflow.\n')
            artifact = record_artifact(self.state, self.opp_id, 'resume', {**self.payload(), 'local_path':str(missing)})
            self.assertEqual(len(artifact['sha256']), 64)
            path = Path(td)/'state.json'; save_state(path, self.state)
            self.assertEqual(load_state(path)['opportunities'][self.opp_id]['application_artifacts'][-1], artifact)


if __name__ == '__main__':
    unittest.main()
