"""Command-line input and output for the note manager."""

from .note_service import NoteService


class NoteCli:
    """Provide the V1 command-line flow for managing notes."""

    def __init__(self, note_service: NoteService) -> None:
        self.note_service = note_service

    def run(self) -> None:
        """Show the menu until the user chooses to exit."""
        print("\n个人笔记管理器")

        while True:
            print("\n1. 新建笔记")
            print("2. 查看笔记")
            print("3. 查看详情")
            print("4. 编辑笔记")
            print("5. 删除笔记")
            print("6. 查找笔记")
            print("0. 退出")
            choice = input("请选择操作：").strip()

            if choice == "1":
                self.create_note()
            elif choice == "2":
                self.list_notes()
            elif choice == "3":
                self.view_note_detail()
            elif choice == "4":
                self.edit_note()
            elif choice == "5":
                self.delete_note()
            elif choice == "6":
                self.search_notes()
            elif choice == "0":
                print("已退出程序。")
                break
            else:
                print("无效选择，请输入 1、2、3、4、5、6 或 0。")

    def create_note(self) -> None:
        """Collect note input and save one note through the service layer."""
        print("\n新建笔记")
        title = input("标题：")
        content = input("正文：")
        tags_text = input("标签（用逗号分隔，可留空）：")
        tags = tags_text.split(",") if tags_text else []

        try:
            note = self.note_service.create_note(
                title=title,
                content=content,
                tags=tags,
            )
        except ValueError as error:
            print(f"创建失败：{error}")
            return

        print(f"笔记已保存，编号：{note.id}")

    def list_notes(self) -> None:
        """Display notes and allow a selected note to be opened."""
        while True:
            notes = self.note_service.list_notes()
            if not notes:
                print("\n暂无笔记。")
                return

            self._display_note_summaries(notes, "笔记列表")

            note_number = self._read_note_number(
                "输入笔记编号查看详情，输入 0 返回主菜单："
            )
            if note_number == 0:
                return
            if self.note_service.get_note_detail(note_number) is None:
                print("未找到该编号的笔记。")
                continue

            self.view_note_detail(note_number)

    def view_note_detail(self, note_number: int | None = None) -> None:
        """Display one note and provide actions for that note."""
        if note_number is None:
            note_number = self._read_note_number("请输入笔记编号（输入 0 返回）：")
            if note_number == 0:
                return

        while True:
            note = self.note_service.get_note_detail(note_number)
            if note is None:
                print("未找到该编号的笔记。")
                return

            tags = note.get("tags", [])
            tags_text = ", ".join(tags) if tags else "无"
            print("\n笔记详情")
            print(f"标题：{note.get('title', '未命名笔记')}")
            print(f"正文：{note.get('content', '')}")
            print(f"标签：{tags_text}")
            print(f"创建时间：{note.get('created_at', '未知')}")
            print(f"更新时间：{note.get('updated_at', '未知')}")
            print("\n1. 编辑当前笔记")
            print("2. 删除当前笔记")
            print("0. 返回")
            choice = input("请选择操作：").strip()

            if choice == "1":
                self.edit_note(note_number)
            elif choice == "2":
                if self.delete_note(note_number):
                    return
            elif choice == "0":
                return
            else:
                print("无效选择，请输入 1、2 或 0。")

    def edit_note(self, note_number: int | None = None) -> bool:
        """Collect replacement values and save changes to one note."""
        if note_number is None:
            note_number = self._select_note_for_action("编辑")
            if note_number is None:
                return False

        note = self.note_service.get_note_detail(note_number)
        if note is None:
            print("未找到该编号的笔记。")
            return False

        print("直接回车保留当前内容；标签输入 - 可清空。")
        title_input = input(f"标题（当前：{note.get('title', '')}）：")
        content_input = input(f"正文（当前：{note.get('content', '')}）：")
        current_tags = ", ".join(note.get("tags", []))
        tags_input = input(f"标签（当前：{current_tags}）：")

        title = title_input if title_input.strip() else note.get("title", "")
        content = content_input if content_input else note.get("content", "")
        if tags_input == "":
            tags = note.get("tags", [])
        elif tags_input.strip() == "-":
            tags = []
        else:
            tags = tags_input.split(",")

        try:
            updated_note = self.note_service.update_note(
                note_number=note_number,
                title=title,
                content=content,
                tags=tags,
            )
        except ValueError as error:
            print(f"编辑失败：{error}")
            return False

        if updated_note is None:
            print("未找到该编号的笔记。")
            return False

        print("笔记已更新。")
        return True

    def delete_note(self, note_number: int | None = None) -> bool:
        """Confirm and delete one selected note."""
        if note_number is None:
            note_number = self._select_note_for_action("删除")
            if note_number is None:
                return False

        note = self.note_service.get_note_detail(note_number)
        if note is None:
            print("未找到该编号的笔记。")
            return False

        title = note.get("title", "未命名笔记")
        confirmation = input(f"确认删除笔记“{title}”？输入 y 确认：").strip().lower()
        if confirmation != "y":
            print("已取消删除。")
            return False

        deleted_note = self.note_service.delete_note(note_number)
        if deleted_note is None:
            print("未找到该编号的笔记。")
            return False

        print("笔记已删除。")
        return True

    def search_notes(self) -> None:
        """Display matching notes and allow a result to be opened."""
        keyword = input("请输入关键词：")
        while True:
            results = self.note_service.search_notes(keyword)
            if not results:
                print("未找到匹配的笔记。")
                return

            result_numbers = {note["note_number"] for note in results}
            self._display_note_summaries(results, "搜索结果")

            note_number = self._read_note_number(
                "输入笔记编号查看详情，输入 0 返回主菜单："
            )
            if note_number == 0:
                return
            if note_number not in result_numbers:
                print("该编号不在当前搜索结果中。")
                continue

            self.view_note_detail(note_number)

    def _select_note_for_action(self, action_name: str) -> int | None:
        """Select a note from the list or from a keyword search."""
        while True:
            notes = self.note_service.list_notes()
            if not notes:
                print("\n暂无笔记。")
                return None

            self._display_note_summaries(notes, f"选择要{action_name}的笔记")
            choice = input(
                "输入笔记编号选择，输入 s 搜索，输入 0 取消："
            ).strip()
            if choice == "0":
                return None
            if choice.casefold() == "s":
                note_number = self._select_search_result_for_action(action_name)
                if note_number is not None:
                    return note_number
                continue

            note_number = self._parse_note_number(choice)
            if note_number is None:
                continue
            if self.note_service.get_note_detail(note_number) is None:
                print("未找到该编号的笔记。")
                continue
            return note_number

    def _select_search_result_for_action(self, action_name: str) -> int | None:
        """Search for a note and return one original note number."""
        while True:
            keyword = input("请输入关键词（输入 0 返回笔记列表）：").strip()
            if keyword == "0":
                return None

            results = self.note_service.search_notes(keyword)
            if not results:
                print("未找到匹配的笔记。")
                continue

            result_numbers = {note["note_number"] for note in results}
            while True:
                self._display_note_summaries(results, f"选择要{action_name}的搜索结果")
                choice = input("输入笔记编号选择，输入 0 返回笔记列表：").strip()
                if choice == "0":
                    return None

                note_number = self._parse_note_number(choice)
                if note_number is None:
                    continue
                if note_number not in result_numbers:
                    print("该编号不在当前搜索结果中。")
                    continue
                return note_number

    @staticmethod
    def _display_note_summaries(notes: list[dict], heading: str) -> None:
        """Display note summaries while preserving their original numbers."""
        print(f"\n{heading}")
        for index, note in enumerate(notes, start=1):
            note_number = note.get("note_number", index)
            tags = note.get("tags", [])
            tags_text = ", ".join(tags) if tags else "无"
            print(f"\n{note_number}. {note.get('title', '未命名笔记')}")
            print(f"   标签：{tags_text}")
            print(f"   更新时间：{note.get('updated_at', '未知')}")

    @staticmethod
    def _read_note_number(prompt: str) -> int:
        """Read a positive note number or zero for returning."""
        while True:
            value = input(prompt).strip()
            try:
                note_number = int(value)
            except ValueError:
                print("笔记编号必须是正整数，或输入 0 返回。")
                continue

            if note_number < 0:
                print("笔记编号必须是正整数，或输入 0 返回。")
                continue
            return note_number

    @staticmethod
    def _parse_note_number(value: str) -> int | None:
        """Parse a positive note number and report invalid values."""
        try:
            note_number = int(value)
        except ValueError:
            print("笔记编号必须是正整数。")
            return None

        if note_number < 1:
            print("笔记编号必须是正整数。")
            return None
        return note_number
