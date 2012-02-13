from django.test import TestCase

from models import *

class TestItem(models.Model):
    field1 = models.CharField(max_length=10)

class TestCategory(DAGCategory):
    items = models.ManyToManyField(TestItem, blank=True)
    
    all_items = lambda self: self._all_subitems(TestItem.objects.all(), 'testcategory')

class DAGTest(TestCase):
    def test_categories_form_a_directed_acyclic_graph(self):
        item = TestItem(field1="foo")
        item.save()
        root = TestCategory(slug="root")
        root.save()
        branch = TestCategory(slug="branch", parent=root)
        branch.save()
        leaf = TestCategory(slug="leaf", parent=branch)
        leaf.save()
        leaf.items.add(item)
        
        self.assertEqual(1, len(root.subcategories()))
        self.assertEqual(1, len(root.subcategories().filter(pk=branch.pk)))
        self.assertEqual(3, len(root.subtree()))
        self.assertEqual(2, len(root.all_children()))
        self.assertEqual(1, len(root.all_children().filter(pk=branch.pk)))
        self.assertEqual(1, len(root.all_children().filter(pk=leaf.pk)))
        
        self.assertEqual(3, len(leaf.branch()))
        self.assertEqual(2, len(leaf.parents()))
        self.assertEqual(2, len(branch.branch()))
        self.assertEqual(1, len(branch.parents().filter(pk=root.pk)))
        
        family = (leaf, branch, root)
        tree = leaf.branch()
        for i in range(3):
            self.assertEqual(family[i].pk, tree[i].pk)
        
        parents = leaf.travel_up()
        for i in range(2):
            self.assertEqual(family[i+1].pk, parents[i].pk)
        
        parents = leaf.parents()
        family = (root, branch)
        for i in range(2):
            self.assertEqual(family[i].pk, parents[i].pk)
        
        self.assertEqual(1, len(root.all_items()))
        
        self.assertNotEqual(-1, root.urllize().find(root.slug))
        self.assertNotEqual(-1, branch.urllize().find(branch.slug))
        self.assertNotEqual(-1, leaf.urllize().find(leaf.slug))
        
        self.assertEqual(1, len(TestCategory.objects.build_tree_structure()))
    
    def test_proper_subtreelookups(self):
        root = TestCategory(slug="root")
        root.save()
        rootroot = TestCategory(slug="rootroot")
        rootroot.save()
        self.assertFalse(root.all_children())
        
