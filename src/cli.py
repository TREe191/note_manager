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
        """Display the basic information for every saved note."""
        notes = self.note_service.list_notes()

        if not notes:
            print("\n暂无笔记。")
            return

        print("\n笔记列表")
        for index, note in enumerate(notes, start=1):
            tags = note.get("tags", [])
            tags_text = ", ".join(tags) if tags else "无"
            print(f"\n{index}. {note.get('title', '未命名笔记')}")
            print(f"   标签：{tags_text}")
            print(f"   更新时间：{note.get('updated_at', '未知')}")

    def view_note_detail(self) -> None:
        """Display all available information for one selected note."""
        note_number_text = input("请输入笔记编号：").strip()

        try:
            note_number = int(note_number_text)
        except ValueError:
            print("笔记编号必须是正整数。")
            return

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

    def edit_note(self) -> None:
        """Collect replacement values and save changes to one note."""
        note_number_text = input("请输入要编辑的笔记编号：").strip()

        try:
            note_number = int(note_number_text)
        except ValueError:
            print("笔记编号必须是正整数。")
            return

        note = self.note_service.get_note_detail(note_number)
        if note is None:
            print("未找到该编号的笔记。")
            return

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
            return

        if updated_note is None:
            print("未找到该编号的笔记。")
            return

        print("笔记已更新。")

    def delete_note(self) -> None:
        """Confirm and delete one selected note."""
        note_number_text = input("请输入要删除的笔记编号：").strip()

        try:
            note_number = int(note_number_text)
        except ValueError:
            print("笔记编号必须是正整数。")
            return

        note = self.note_service.get_note_detail(note_number)
        if note is None:
            print("未找到该编号的笔记。")
            return

        title = note.get("title", "未命名笔记")
        confirmation = input(f"确认删除笔记“{title}”？输入 y 确认：").strip().lower()
        if confirmation != "y":
            print("已取消删除。")
            return

        deleted_note = self.note_service.delete_note(note_number)
        if deleted_note is None:
            print("未找到该编号的笔记。")
            return

        print("笔记已删除。")

    def search_notes(self) -> None:
        """Collect a keyword and display matching note summaries."""
        keyword = input("请输入关键词：")
        results = self.note_service.search_notes(keyword)

        if not results:
            print("未找到匹配的笔记。")
            return

        print("\n搜索结果")
        for note in results:
            tags = note.get("tags", [])
            tags_text = ", ".join(tags) if tags else "无"
            print(f"\n{note['note_number']}. {note.get('title', '未命名笔记')}")
            print(f"   标签：{tags_text}")
