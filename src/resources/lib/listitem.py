# -*- coding: utf-8 -*-
from __future__ import absolute_import

from xbmcgui import ListItem

from resources.lib.routing import plugin
from resources.lib.settings import settings


class ExtendedListItem(ListItem):
    def __new__(cls, name, label2="", iconImage="", thumbnailImage="", path="", **kwargs):
        return super(ExtendedListItem, cls).__new__(
            cls, name, label2, iconImage, thumbnailImage, path
        )

    def __init__(
        self,
        name,
        label2="",
        iconImage="",
        thumbnailImage="",
        path="",
        poster=None,
        video_info=None,
        properties=None,
        addContextMenuItems=False,
        subtitles=None,
    ):
        super(ExtendedListItem, self).__init__(name, label2, iconImage, thumbnailImage, path)
        if properties:
            self.setProperties(**properties)
        if video_info:
            self.setInfo("video", video_info)
            self.setResumeTime(video_info.get("time"))
        if poster:
            self.setArt({"poster": poster})
        if subtitles:
            self.setSubtitles(subtitles)
        if addContextMenuItems:
            self.addPredefinedContextMenuItems()

    def _addWatchlistContextMenuItem(self, menu_items):
        in_watchlist = self.getProperty("in_watchlist")
        if in_watchlist == "":
            return
        label = "Не буду смотреть" if int(in_watchlist) else "Буду смотреть"
        url = plugin.build_url(
            "toggle_watchlist", self.getProperty("id"), int(not int(in_watchlist))
        )
        menu_items.append((label, "Container.Update({})".format(url)))

    def _addWatchedContextMenuItem(self, menu_items):
        item_id = self.getProperty("id")
        season_number = self.getVideoInfoTag().getSeason()
        video_number = self.getVideoInfoTag().getEpisode()
        video_number = video_number if video_number != -1 else 1
        watched = int(self.getVideoInfoTag().getPlayCount()) > 0
        label = "Отметить как непросмотренное" if watched else "Отметить как просмотренное"
        if self.getVideoInfoTag().getMediaType() == "tvshow":
            return
        elif self.getVideoInfoTag().getMediaType() == "season":
            kwargs = {"season": season_number}
        elif self.getProperty("subtype") == "multi":
            kwargs = {}
        elif season_number != -1:
            kwargs = {"season": season_number, "video": video_number}
        else:
            kwargs = {"video": video_number}
        url = plugin.build_url("toggle_watched", item_id, **kwargs)
        menu_items.append((label, "Container.Update({})".format(url)))

    def _addBookmarksContextMenuItem(self, menu_items):
        if self.getVideoInfoTag().getMediaType() == "season":
            return
        item_id = self.getProperty("id")
        label = "Изменить закладки"
        url = plugin.build_url("edit_bookmarks", item_id)
        menu_items.append((label, "Container.Update({})".format(url)))

    def _addCommentsContextMenuItem(self, menu_items):
        item_id = self.getProperty("id")
        label = "Комментарии KinoPub"
        url = plugin.build_url("comments", item_id)
        menu_items.append((label, "Container.Update({})".format(url)))

    def _addSimilarContextMenuItem(self, menu_items):
        item_id = self.getProperty("id")
        title = self.getLabel()
        label = "Похожие фильмы"
        url = plugin.build_url("similar", item_id, title=title)
        menu_items.append((label, u"Container.Update({})".format(url)))

    def _addSeparatorContextMenuItem(self, menu_items):
        # 21 is the maximum number of characters when the horizontal scrolling doesn't appear.
        menu_items.append(("─" * 21, ""))

    def addPredefinedContextMenuItems(self, items=None):
        items = items or ["watched", "watchlist", "bookmarks", "comments", "similar", "separator"]
        menu_items = []
        for item in items:
            getattr(self, "_add{}ContextMenuItem".format(item.capitalize()))(menu_items)
        self.addContextMenuItems(menu_items)

    def setProperties(self, **properties):
        for prop, value in properties.items():
            self.setProperty(prop, str(value))

    def setResumeTime(self, resumetime, totaltime=None):
        totaltime = float(totaltime or self.getduration())
        if (
            resumetime is not None
            and totaltime > 0
            and 100 * resumetime / totaltime
            <= settings.advanced("video", "playcountminimumpercent")
            and resumetime > settings.advanced("video", "ignoresecondsatstart")
            or resumetime == 0
        ):
            self.setProperties(resumetime=resumetime, totaltime=totaltime)

    def markAdvert(self, has_advert):
        if settings.mark_advert == "true" and has_advert:
            self.setLabel("{} (!)".format(self.getLabel()))
