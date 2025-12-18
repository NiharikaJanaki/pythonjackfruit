# gui.py (corrected & improved)

import wx
import wx.adv
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from storage import (
    load_groceries,
    load_recipes,
    save_user_purchase,
    load_user_purchases,
    get_expiring_items,
    find_recipes_using_items,
    DATE_FMT,
)


class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(parent, title="Freshmate", size=(900, 660))
        panel = wx.Panel(self)

        # Load data
        self.groceries = load_groceries()
        self.recipes = load_recipes()
        self.user_purchases = load_user_purchases()

        # Layout - use sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Purchase entry panel ---
        pnl_entry = wx.StaticBoxSizer(wx.StaticBox(panel, label="Add Purchase"), wx.VERTICAL)
        grid = wx.FlexGridSizer(2, 4, 8, 8)
        grid.AddGrowableCol(1)

        grid.Add(wx.StaticText(panel, label="Item:"), 0, wx.ALIGN_CENTER_VERTICAL)
        # show display-friendly choices (sorted)
        choices = sorted(self.groceries.keys())
        self.item_choice = wx.ComboBox(panel, choices=choices, style=wx.CB_DROPDOWN)
        grid.Add(self.item_choice, 1, wx.EXPAND)

        grid.Add(wx.StaticText(panel, label="Purchase date:"), 0, wx.ALIGN_CENTER_VERTICAL)
        self.date_picker = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        grid.Add(self.date_picker, 1, wx.EXPAND)

        add_btn = wx.Button(panel, label="Add & Save")
        add_btn.Bind(wx.EVT_BUTTON, self.on_add_purchase)
        grid.Add(add_btn, 0)

        clear_btn = wx.Button(panel, label="Clear Purchases File")
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear_purchases)
        grid.Add(clear_btn, 0)

        pnl_entry.Add(grid, 0, wx.ALL | wx.EXPAND, 8)
        main_sizer.Add(pnl_entry, 0, wx.ALL | wx.EXPAND, 8)

        # --- Purchases list ---
        pnl_list = wx.StaticBoxSizer(wx.StaticBox(panel, label="Current Purchases (latest per item)"), wx.VERTICAL)
        self.purchases_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.purchases_list.InsertColumn(0, "Item", width=200)
        self.purchases_list.InsertColumn(1, "Purchase Date", width=140)
        self.purchases_list.InsertColumn(2, "Expiry Date", width=140)
        pnl_list.Add(self.purchases_list, 1, wx.ALL | wx.EXPAND, 6)
        main_sizer.Add(pnl_list, 0, wx.ALL | wx.EXPAND, 8)

        # --- Expiry check panel ---
        pnl_check = wx.StaticBoxSizer(wx.StaticBox(panel, label="Check Expiry & Recipes"), wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(wx.StaticText(panel, label="Check date:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.check_date_picker = wx.adv.DatePickerCtrl(panel, style=wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        hbox.Add(self.check_date_picker, 0, wx.RIGHT, 10)

        self.check_within = wx.SpinCtrl(panel, value="2", min=0, max=30)
        hbox.Add(wx.StaticText(panel, label="Within days:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        hbox.Add(self.check_within, 0, wx.LEFT | wx.RIGHT, 6)

        check_btn = wx.Button(panel, label="Check Expiring Items")
        check_btn.Bind(wx.EVT_BUTTON, self.on_check_expiry)
        hbox.Add(check_btn, 0, wx.LEFT, 8)

        pnl_check.Add(hbox, 0, wx.ALL | wx.EXPAND, 8)

        # Results area: four panels side-by-side (Expiring, Expired, Recipes OK, Recipes need buy)
        results_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Expiring items
        v1 = wx.BoxSizer(wx.VERTICAL)
        v1.Add(wx.StaticText(panel, label="Expiring Items (soon)"), 0, wx.BOTTOM, 4)
        self.exp_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.exp_list.InsertColumn(0, "Item", width=140)
        self.exp_list.InsertColumn(1, "Expiry Date", width=120)
        v1.Add(self.exp_list, 1, wx.EXPAND | wx.RIGHT, 6)
        results_sizer.Add(v1, 1, wx.EXPAND)

        # Expired items
        v_exp = wx.BoxSizer(wx.VERTICAL)
        v_exp.Add(wx.StaticText(panel, label="Expired Items"), 0, wx.BOTTOM, 4)
        self.expired_list = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.expired_list.InsertColumn(0, "Item", width=140)
        self.expired_list.InsertColumn(1, "Expiry Date", width=120)
        v_exp.Add(self.expired_list, 1, wx.EXPAND | wx.RIGHT, 6)
        results_sizer.Add(v_exp, 1, wx.EXPAND)

        # Recipes available (all ingredients present)
        v2 = wx.BoxSizer(wx.VERTICAL)
        v2.Add(wx.StaticText(panel, label="Recipes You Can Make (all ingredients present)"), 0, wx.BOTTOM, 4)
        self.rec_ok = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.rec_ok.InsertColumn(0, "Recipe", width=150)
        self.rec_ok.InsertColumn(1, "Ingredients", width=260)
        v2.Add(self.rec_ok, 1, wx.EXPAND | wx.RIGHT, 6)
        results_sizer.Add(v2, 2, wx.EXPAND)

        # Recipes need buy (missing listed)
        v3 = wx.BoxSizer(wx.VERTICAL)
        v3.Add(wx.StaticText(panel, label="Recipes That Need Items (missing listed)"), 0, wx.BOTTOM, 4)
        self.rec_need = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.rec_need.InsertColumn(0, "Recipe", width=150)
        self.rec_need.InsertColumn(1, "Missing Items", width=260)
        v3.Add(self.rec_need, 1, wx.EXPAND)
        results_sizer.Add(v3, 2, wx.EXPAND)

        pnl_check.Add(results_sizer, 1, wx.ALL | wx.EXPAND, 6)
        main_sizer.Add(pnl_check, 1, wx.ALL | wx.EXPAND, 8)

        # Bottom status
        self.status = wx.StaticText(panel, label="Ready.")
        main_sizer.Add(self.status, 0, wx.ALL | wx.EXPAND, 8)

        panel.SetSizer(main_sizer)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # populate UI lists
        self.refresh_purchases_list()

    # ---------- events ----------
    def on_add_purchase(self, event):
        item = (self.item_choice.GetValue() or "").strip().lower()
        if not item:
            wx.MessageBox("Choose an item to add.", "Error", wx.ICON_ERROR)
            return

        # Read datepicker and convert to YYYY-MM-DD using FormatISODate()
        d = self.date_picker.GetValue()
        try:
            dt_text = d.FormatISODate()  # reliable cross-platform
        except Exception:
            # fallback to today's date
            dt_text = datetime.now().strftime(DATE_FMT)

        # Save
        save_user_purchase(item, dt_text)
        # reload purchases and refresh list
        self.user_purchases = load_user_purchases()
        self.refresh_purchases_list()
        self.status.SetLabel(f"Saved: {item} @ {dt_text}")

    def on_clear_purchases(self, event):
        try:
            p = Path("user_purchases.csv")
            if p.exists():
                p.unlink()
            self.user_purchases = {}
            self.refresh_purchases_list()
            self.status.SetLabel("Cleared user_purchases.csv")
        except Exception as e:
            wx.MessageBox(f"Failed to clear purchases: {e}", "Error", wx.ICON_ERROR)

    def refresh_purchases_list(self):
        # reload purchases and display latest per item
        self.user_purchases = load_user_purchases()
        self.purchases_list.DeleteAllItems()
        for item, dt in sorted(self.user_purchases.items()):
            shelf = self.groceries.get(item, None)
            expiry_str = "-"
            if shelf is not None:
                expiry_dt = dt + timedelta(days=shelf)
                expiry_str = expiry_dt.strftime(DATE_FMT)
            idx = self.purchases_list.InsertItem(self.purchases_list.GetItemCount(), item)
            self.purchases_list.SetItem(idx, 1, dt.strftime(DATE_FMT))
            self.purchases_list.SetItem(idx, 2, expiry_str)

    def on_check_expiry(self, event):
        # get date from date picker
        d = self.check_date_picker.GetValue()
        try:
            check_date = datetime.strptime(d.FormatISODate(), DATE_FMT)
        except Exception:
            # fallback to today
            check_date = datetime.now()

        within = int(self.check_within.GetValue())

        # load current purchases & compute expiring and expired
        purchases = load_user_purchases()
        expiring, expired = get_expiring_items(check_date, self.groceries, purchases, within_days=within)

        # fill exp_list
        self.exp_list.DeleteAllItems()
        exp_items = []
        for item, expiry in expiring:
            idx = self.exp_list.InsertItem(self.exp_list.GetItemCount(), item)
            self.exp_list.SetItem(idx, 1, expiry.strftime(DATE_FMT))
            exp_items.append(item)

        # fill expired_list
        self.expired_list.DeleteAllItems()
        expired_items = []
        for item, expiry in expired:
            idx = self.expired_list.InsertItem(self.expired_list.GetItemCount(), item)
            self.expired_list.SetItem(idx, 1, expiry.strftime(DATE_FMT))
            expired_items.append(item)

        # find recipes (pass expired items so they are excluded by storage logic)
        possible, need_buy = find_recipes_using_items(exp_items, expired_items, list(purchases.keys()), self.recipes)

        # populate rec_ok and rec_need tables
        self.rec_ok.DeleteAllItems()
        self.rec_need.DeleteAllItems()

        for r in possible:
            i = self.rec_ok.InsertItem(self.rec_ok.GetItemCount(), r["recipe"])
            self.rec_ok.SetItem(i, 1, ", ".join(r["ingredients"]))

        for r in need_buy:
            i = self.rec_need.InsertItem(self.rec_need.GetItemCount(), r["recipe"])
            self.rec_need.SetItem(i, 1, ", ".join(r["missing"]))

        self.status.SetLabel(
            f"Found {len(exp_items)} expiring item(s), {len(possible)} ready recipes, {len(need_buy)} recipes needing purchase, {len(expired_items)} expired."
        )

    def on_close(self, event):
        self.Destroy()


if __name__ == "__main__":
    app = wx.App(redirect=False)
    frm = MainFrame(None)
    frm.Show()
    app.MainLoop()
