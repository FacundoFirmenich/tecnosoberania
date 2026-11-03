"""Unit tests with explicitly invented inputs used ONLY to probe code, not as data/evidence."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine.spse import (EventStore, PolicyError, CapabilityRegistry, Capability,
                         conditional_cashflow)

NOW = datetime(2026, 11, 3, 11, tzinfo=timezone.utc)
def iso(d=NOW): return d.isoformat()

class ConstitutionAndSPSETests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = EventStore(Path(self.tmp.name)/'ledger.sqlite')
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def grant(self, **params):
        return self.db.add_grant(subject='subject', actor='authorized_person', scope='spse.dispatch',
                                 issuer_basis='external_basis_asserted_for_test', verified=True,
                                 valid_from=iso(NOW-timedelta(days=1)), **params)
    def event(self, action, ident):
        return self.db.record_medication_response(subject='subject', episode='med#2026-11-03',
             action=action,interaction_id=ident,observed_at=iso(),recipient_id='contact',
             plan_version='user_entered_version')

    def test_no_family_root_by_default(self):
        self.assertFalse(self.db.authorized('subject','daughter','spse.dispatch'))
    def test_authorized_only_if_verified(self):
        self.db.add_grant(subject='subject',actor='authorized_person',scope='spse.dispatch',
             issuer_basis='claim',verified=False,valid_from=iso(NOW-timedelta(days=1)))
        self.assertFalse(self.db.authorized('subject','authorized_person','spse.dispatch'))
    def test_scope_must_be_exact(self):
        self.grant()
        self.assertFalse(self.db.authorized('subject','authorized_person','bank.pay'))
    def test_grant_and_revoke(self):
        g=self.grant()
        self.assertTrue(self.db.authorized('subject','authorized_person','spse.dispatch'))
        self.assertTrue(self.db.revoke_grant(g))
        self.assertFalse(self.db.authorized('subject','authorized_person','spse.dispatch'))
        self.assertFalse(self.db.revoke_grant(g))
    def test_future_grant_not_live(self):
        self.db.add_grant(subject='subject',actor='a',scope='x',issuer_basis='basis',verified=True,
               valid_from=iso(NOW+timedelta(days=5)))
        self.assertFalse(self.db.authorized('subject','a','x',at=iso(NOW)))
    def test_naive_timestamps_disallowed(self):
        with self.assertRaises(PolicyError):
            self.db.add_grant(subject='s',actor='a',scope='x',issuer_basis='x',verified=True,valid_from='2026-11-03T11:00')
    def test_one_negative_no_incident(self):
        self.assertIsNone(self.event('refused','ref1'))
    def test_two_distinct_negatives_incident(self):
        self.event('refused','ref1')
        issue=self.event('deferred','ref2')
        self.assertEqual(issue.status,'local_intent_only')
        self.assertEqual(issue.recipient_id,'contact')
    def test_no_answer_not_negative(self):
        self.event('unconfirmed','q1');self.event('unconfirmed','q2');self.assertIsNone(self.event('refused','q3'))
    def test_repeated_interaction_dedup(self):
        self.event('refused','ref1')
        self.assertIsNone(self.event('deferred','ref1'))
        self.assertIsNone(self.event('unconfirmed','ref2'))
        self.assertIsNotNone(self.event('refused','ref3'))
    def test_taken_prior_negative_reject(self):
        self.event('taken_self_reported','taken')
        with self.assertRaises(PolicyError):self.event('refused','next')
    def test_incomplete_receipt_rejected(self):
        self.event('refused','ref1');issue=self.event('refused','ref2')
        with self.assertRaises(PolicyError):self.db.transition_incident(issue.incident_id,'queued',actor='nobody',subject='subject')
    def test_receipt_evidence_and_order(self):
        self.event('refused','ref1');i=self.event('refused','ref2');self.grant()
        with self.assertRaises(PolicyError):self.db.transition_incident(i.incident_id,'delivered',actor='authorized_person',subject='subject')
        self.db.transition_incident(i.incident_id,'queued',actor='authorized_person',subject='subject')
        with self.assertRaises(PolicyError):self.db.transition_incident(i.incident_id,'provider_accepted',actor='authorized_person',subject='subject')
        st=self.db.transition_incident(i.incident_id,'provider_accepted',actor='authorized_person',subject='subject',evidence='receipt_from_test_fixture')
        self.assertEqual(st.status,'provider_accepted')
    def test_event_idempotence(self):
        a,first=self.db.append_event(subject='subject',kind='task.created',source='user_reported',observed_at=iso(),interaction_id='same',payload={'title':'test'})
        b,next_=self.db.append_event(subject='subject',kind='task.created',source='user_reported',observed_at=iso(),interaction_id='same',payload={'title':'test'})
        self.assertEqual(a,b);self.assertTrue(first);self.assertFalse(next_)
    def test_sqlite_durable(self):
        self.db.append_event(subject='subject',kind='task.created',source='user_reported',observed_at=iso(),interaction_id='id',payload={'x':1})
        self.db.close();self.db=EventStore(Path(self.tmp.name)/'ledger.sqlite')
        self.assertEqual(self.db.list_events('subject')[0]['payload']['x'],1)
    def test_different_subject_separated(self):
        self.db.append_event(subject='a',kind='task.created',source='user_reported',observed_at=iso(),interaction_id='same',payload={})
        self.db.append_event(subject='b',kind='task.created',source='user_reported',observed_at=iso(),interaction_id='same',payload={})
        self.assertEqual(len(self.db.list_events('a')),1)

class CapabilityAndForecastTests(unittest.TestCase):
    def test_unknown_capability_fail_closed(self):
        self.assertFalse(CapabilityRegistry().can_route('unknown','ES',frozenset()))
    def test_experimental_not_executable(self):
        c=Capability('tag.sound','tagvendor','experimental','tag.control',('ES',),None,('no api verified',))
        r=CapabilityRegistry();r.register(c)
        self.assertFalse(r.can_route('tag.sound','ES',frozenset({'tag.control'})))
    def test_verified_requires_timestamp(self):
        with self.assertRaises(PolicyError):CapabilityRegistry().register(Capability('sound','vendor','verified','tag.control',('ES',),None,()))
    def test_region_scoped(self):
        r=CapabilityRegistry();r.register(Capability('sound','vendor','verified','tag.control',('ES',),iso(),()))
        self.assertTrue(r.can_route('sound','ES',frozenset({'tag.control'})))
        self.assertFalse(r.can_route('sound','AR',frozenset({'tag.control'})))
    def test_missing_scope_reject(self):
        r=CapabilityRegistry();r.register(Capability('a','vendor','verified','scope',(),iso(),()))
        self.assertFalse(r.can_route('a','ES',frozenset()))
    def test_decimal_projection_exact(self):
        v=conditional_cashflow(currency='EUR',cash='500',monthly_income='120.50',monthly_outflows='80.25',months=2,exceptional='40',reserve='100')
        self.assertEqual(v['balance'],'540.50');self.assertEqual(v['available_above_reserve'],'440.50')
    def test_missing_projection_fails(self):
        with self.assertRaises(PolicyError):conditional_cashflow(currency='EUR',cash=None,monthly_income='1',monthly_outflows='0',months=2,exceptional='0',reserve='0')
    def test_naive_prediction_not_claimed(self):
        v=conditional_cashflow(currency='ARS',cash='1',monthly_income='1',monthly_outflows='0',months=1,exceptional='0',reserve='0')
        self.assertIn('not_a_forecast',v['kind'])
    def test_bad_months_reject(self):
        with self.assertRaises(PolicyError):conditional_cashflow(currency='EUR',cash='1',monthly_income='1',monthly_outflows='0',months=1201,exceptional='0',reserve='0')
    def test_nonfinite_reject(self):
        with self.assertRaises(PolicyError):conditional_cashflow(currency='EUR',cash='Infinity',monthly_income='1',monthly_outflows='0',months=1,exceptional='0',reserve='0')

if __name__=='__main__':unittest.main(verbosity=2)