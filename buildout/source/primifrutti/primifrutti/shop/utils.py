from product.models import Category
from django.utils.datastructures import SortedDict



class CategoriesPortlet(object):
    """ API for categories portlet html rendering """

    def __init__(self, context):
        self.context = context
        
    def render(self):
        product = self.context.get("product", None)
        category = self.context.get("category", None)

        if product:
            cats = product.category.all()

            if cats:
                category = cats[0]

        if not category:
            categories = SortedDict()
            first_level_categories = Category.objects.filter(
                parent__isnull=True, is_active=True).order_by('ordering', 'name')

            for item in first_level_categories:
                categories[item.pk] = SortedDict({
                    'name': item.name,
                    'slug': item.slug,
                    'url': item.get_absolute_url(),
                    'subcategories': {},
                    'current': False})

            return {'menu': self.asHtml(categories),
                'categories': categories.values()}

        else:
            internal_categories = self.look_for_category(
                category, category.id)

            html_categories = self.asHtml(internal_categories)
            return {'menu': html_categories,
                'categories': internal_categories.values()}

    def renderNode(self, node, url):
        if not node:
            return ""

        nodes = []
        for key, values in node['subcategories'].iteritems():
            nodes.append(self.renderNode(values, values['url']))

        result = "".join(nodes)

        if result:
            return """<li><a %(class)s title="%(name)s" \
                href="%(href)s"><span>%(name)s</span></a> \
                <ul>%(result)s</ul></li>""" % {
                'class': node['current'] and "class='navTreeCurrentItem'" or '',
                'href': url,
                'name': node['name'],
                'result': result}
        else:
            return """<li><a %(class)s title="%(name)s" \
                href="%(href)s"><span>%(name)s</span></a></li>""" % {
                'class': node['current'] and "class='navTreeCurrentItem'" or '',
                'href': url,
                'name': node['name']}


    def asHtml(self, menu):
        nodes = []
        for key, value in menu.iteritems():
            nodes.append(self.renderNode(value, value['url']))

        return """<ul class="nav nav-list">%(nodes)s</ul>""" % {
            'nodes': "".join(nodes)}

    def look_for_category(self, category, category_id, struct=None):
        """ Recursive method for categories html struct constuction """
        if category_id:
            main_category = Category.objects.get(id=category_id)
            parent = main_category.parent

            same_level = SortedDict()

            if struct == None:
                struct = SortedDict()

            if parent:
                parent_id = parent.id
            else:
                parent_id = None

            if parent_id:
                same_level_categories = Category.objects.filter(
                    parent__id=parent_id, is_active=True).order_by('ordering', 'name')
            else:
                same_level_categories = Category.objects.filter(
                    parent__isnull=True, is_active=True).order_by('ordering', 'name')

            for item in same_level_categories:
                same_level[item.pk] = {
                    'name': item.name,
                    'slug': item.slug,
                    'url': item.get_absolute_url(),
                    'subcategories': SortedDict(),
                    'current': (main_category.pk == item.pk) and True or False}

                if same_level[item.pk]['current']:
                    contents = Category.objects.filter(
                        parent__id=item.id, is_active=True).order_by('ordering', 'name')

                    if contents.count():
                        for content_item in contents:
                            same_level[item.pk]['subcategories'].update(
                                SortedDict({
                                content_item.pk: SortedDict({
                                    'name': content_item.name,
                                    'slug': content_item.slug,
                                    'url': content_item.get_absolute_url(),
                                    'subcategories': SortedDict(),
                                    'current': False})}))

                if main_category.id == item.id and struct != {}:
                    same_level[item.pk]["subcategories"].update(struct)
            if parent_id:
                return self.look_for_category(category, parent_id, same_level)
            else:
                return same_level
