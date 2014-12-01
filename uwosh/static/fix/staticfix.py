from plone.portlet.static import static
from lxml import etree
from lxml import html
from Products.CMFCore.utils import getToolByName

class Renderer(static.Renderer):
    """Portlet renderer.
    Patch to fix relative links.  This class will reconstruct the links.  The 
    link reconstruction will be determined by where the portlet was originally assigned.
    """
    
    def transformed(self, mt='text/x-html-safe'):
        results = static.Renderer.transformed(self,mt)
        
        self._portlet = None
        portlets = self.manager(self.context,self.request,self.view).portletsToShow()
        for portlet in portlets:
            if portlet['name'] == self.data.id:
                self._portlet = portlet
                
        if self._portlet == None:
            return results
        return self._reconstruct(results)
            
            
    def _reconstruct(self,text):
        nodes  = html.fragment_fromstring(text.strip(), create_parent=True)
        for node in nodes.xpath('//*[@href]'):
            url = self._relative_to_absolute(node.get('href'))
            node.set('href', url)
        return etree.tostring(nodes, pretty_print=False, encoding="utf-8")
    
        
    def _relative_to_absolute(self,url):
        """
        If root is already absolute, return it.  Otherwise, turn relative link to 
        absolute.  First get plone site_root, second get location where portlet was
        assigned, third small clean of merging of URL's.  
        """
        if '://' in url or 'mailto:' in url:
            return url
        else:
            site_root = getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()
            root = site_root[site_root.rfind('/'):len(str(site_root))]
            portlet_root = self._portlet['key'][self._portlet['key'].rfind(root)+len(root):len(self._portlet['key'])]
            return site_root + '/'.join([portlet_root,url])
