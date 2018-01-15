from .context import esb
import unittest
import copy


class BasicTestSuite(unittest.TestCase):
    """Some tests of basic package functionality."""

    @classmethod
    def setUpClass(cls):
        super(BasicTestSuite, cls).setUpClass()
        cls.sc = esb.StatementClassifier.StatementClassifier()
        cls.sc.load_training("./data/labels-training/esb_training_full.csv")
        cls.sc.train()
        cls.tc = esb.TokenClassifier.TokenClassifier()
        cls.tc.load_training("./data/labels-training/esb_training_full.csv")
        cls.tc.train()
        cls.records = esb.Utils.Utils.auto_load()

    def test_sc_labeler_returns_record(self):
        self.assertIsInstance(
            self.sc.label(
                self.records[0]),
            esb.Record.Record)

    def test_record_remarks(self):
        self.assertEqual(
            self.sc.label(
                self.records[0]).remarks(),
            "She Nat of Ferrymount, 6 miles from Mt Mellick, Queens, Ire - Arr Jul 1844 per Fairfield from LP - Fa in Ire John Henry, Mo dead Bridget Fahy, 4 Bros Pat'k, John & James in US, Martin in Ire, 3 Sis Ellen, Honora & ___ see 3989")

    def test_sc_labeled_record_has_statement_labels(self):
        record = copy.copy(self.records[0])
        self.assertTrue(len(self.sc.label(record).statement_labels) > 0)

    def test_sc_labeled_record_does_not_have_token_labels(self):
        record = copy.copy(self.records[0])
        self.assertIsNone(self.sc.label(record).token_labels)

    def test_tc_labeled_record_has_token_labels(self):
        record = copy.copy(self.records[0])
        self.assertTrue(
            len(self.tc.label(self.sc.label(record)).token_labels) > 0)

    def test_can_construct_parse_tree_on_labeled_record(self):
        record = copy.copy(self.records[0])
        record = self.tc.label(self.sc.label(record))
        pt = esb.SequenceParser.SequenceParser.create_parse_tree(record)
        self.assertIsInstance(pt, esb.ParseTree.TreeNode)

    def test_parse_tree_root_has_children(self):
        record = copy.copy(self.records[0])
        record = self.tc.label(self.sc.label(record))
        pt = esb.SequenceParser.SequenceParser.create_parse_tree(record)
        self.assertTrue(len(pt.children) > 0)

    def test_parse_tree_children_are_tree_nodes(self):
        record = copy.copy(self.records[0])
        record = self.tc.label(self.sc.label(record))
        pt = esb.SequenceParser.SequenceParser.create_parse_tree(record)
        self.assertIsInstance(pt.children[0], esb.ParseTree.TreeNode)

    def test_full_extraction_of_record(self):
        record = copy.copy(self.records[13000])
        extracted_record = esb.SequenceParser.SequenceParser.process_completely(
            record, self.tc, self.sc)
        self.assertTrue(
            'extracted' in extracted_record and 'original' in extracted_record)


if __name__ == '__main__':
    unittest.main()
