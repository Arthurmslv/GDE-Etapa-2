import sys
import sqlite3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from main_ui import MainUI
from task_ui import TaskUI


class Main(MainUI):

    def __init__(self):
        super().__init__()

        self.conexao = sqlite3.connect(
            "gestor_estudos.db"
        )

        self.cursor = self.conexao.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            disciplina TEXT,
            data TEXT,
            prioridade TEXT,
            status TEXT,
            descricao TEXT
        )
        """)

        self.conexao.commit()

        self.carregar_tarefas()

        self.btnNova.clicked.connect(
            self.abrir_tarefa
        )

        self.btnConcluir.clicked.connect(
            self.concluir_tarefa
        )

        self.btnExcluir.clicked.connect(
            self.excluir_tarefa
        )

        self.btnEditar.clicked.connect(
            self.editar_tarefa
        )

        self.tabela.cellDoubleClicked.connect(
            self.mostrar_descricao
        )

    def abrir_tarefa(self):

        janela = TaskUI()

        janela.salvar.clicked.connect(
            lambda: self.salvar_tarefa(
                janela
            )
        )

        janela.exec_()

    def salvar_tarefa(self, janela):

        titulo = janela.titulo.text()

        disciplina = janela.disciplina.text()

        prioridade = janela.prioridade.currentText()

        data = janela.data.date().toString(
            "dd/MM/yyyy"
        )

        descricao = janela.descricao.toPlainText()

        if titulo == "":
            return

        self.cursor.execute("""
        INSERT INTO tarefas(
            titulo,
            disciplina,
            data,
            prioridade,
            status,
            descricao
        )
        VALUES(?,?,?,?,?,?)
        """, (
            titulo,
            disciplina,
            data,
            prioridade,
            "Pendente",
            descricao
        ))

        self.conexao.commit()

        id_tarefa = self.cursor.lastrowid

        linha = self.tabela.rowCount()

        self.tabela.insertRow(
            linha
        )

        self.adicionar_item(
            linha,
            0,
            titulo
        )

        self.adicionar_item(
            linha,
            1,
            disciplina
        )

        self.adicionar_item(
            linha,
            2,
            data
        )

        self.adicionar_item(
            linha,
            3,
            prioridade
        )

        self.adicionar_item(
            linha,
            4,
            "Pendente"
        )

        self.tabela.item(
            linha,
            0
        ).setData(
            Qt.UserRole,
            {
                "id": id_tarefa,
                "descricao": descricao
            }
        )

        self.atualizar_estatisticas()

        janela.close()

    def adicionar_item(
        self,
        linha,
        coluna,
        texto
    ):

        item = QTableWidgetItem(
            texto
        )

        item.setTextAlignment(
            Qt.AlignCenter
        )

        self.tabela.setItem(
            linha,
            coluna,
            item
        )

    def carregar_tarefas(self):

        self.tabela.setRowCount(
            0
        )

        self.cursor.execute(
            "SELECT * FROM tarefas"
        )

        tarefas = self.cursor.fetchall()

        for tarefa in tarefas:

            id_tarefa = tarefa[0]

            titulo = tarefa[1]

            disciplina = tarefa[2]

            data = tarefa[3]

            prioridade = tarefa[4]

            status = tarefa[5]

            descricao = tarefa[6]

            linha = self.tabela.rowCount()

            self.tabela.insertRow(
                linha
            )

            self.adicionar_item(
                linha,
                0,
                titulo
            )

            self.adicionar_item(
                linha,
                1,
                disciplina
            )

            self.adicionar_item(
                linha,
                2,
                data
            )

            self.adicionar_item(
                linha,
                3,
                prioridade
            )

            self.adicionar_item(
                linha,
                4,
                status
            )

            self.tabela.item(
                linha,
                0
            ).setData(
                Qt.UserRole,
                {
                    "id": id_tarefa,
                    "descricao": descricao
                }
            )

        self.atualizar_estatisticas()

    def mostrar_descricao(
        self,
        linha
    ):

        dados = self.tabela.item(
            linha,
            0
        ).data(
            Qt.UserRole
        )

        descricao = dados["descricao"]

        if descricao == "":

            descricao = "Sem descrição"

        QMessageBox.information(
            self,
            "Descrição da tarefa",
            descricao
        )

    def excluir_tarefa(self):

        linha = self.tabela.currentRow()

        if linha < 0:
            return

        resposta = QMessageBox.question(
            self,
            "Excluir",
            "Deseja excluir esta tarefa?",
            QMessageBox.Yes |
            QMessageBox.No
        )

        if resposta == QMessageBox.Yes:

            dados = self.tabela.item(
                linha,
                0
            ).data(
                Qt.UserRole
            )

            self.cursor.execute(
                "DELETE FROM tarefas WHERE id=?",
                (
                    dados["id"],
                )
            )

            self.conexao.commit()

            self.tabela.removeRow(
                linha
            )

            self.atualizar_estatisticas()

    def editar_tarefa(self):

        linha = self.tabela.currentRow()

        if linha < 0:
            return

        janela = TaskUI()

        dados = self.tabela.item(
            linha,
            0
        ).data(
            Qt.UserRole
        )

        titulo = self.tabela.item(
            linha,
            0
        ).text()

        disciplina = self.tabela.item(
            linha,
            1
        ).text()

        prioridade = self.tabela.item(
            linha,
            3
        ).text()

        descricao = dados["descricao"]

        janela.titulo.setText(
            titulo
        )

        janela.disciplina.setText(
            disciplina
        )

        janela.prioridade.setCurrentText(
            prioridade
        )

        janela.descricao.setText(
            descricao
        )

        janela.salvar.clicked.connect(
            lambda: self.atualizar_tarefa(
                janela,
                linha,
                dados["id"]
            )
        )

        janela.exec_()

    def atualizar_tarefa(
        self,
        janela,
        linha,
        id_tarefa
    ):

        titulo = janela.titulo.text()

        disciplina = janela.disciplina.text()

        prioridade = janela.prioridade.currentText()

        data = janela.data.date().toString(
            "dd/MM/yyyy"
        )

        descricao = janela.descricao.toPlainText()

        status = self.tabela.item(
            linha,
            4
        ).text()

        self.cursor.execute("""
        UPDATE tarefas
        SET
            titulo=?,
            disciplina=?,
            data=?,
            prioridade=?,
            status=?,
            descricao=?
        WHERE id=?
        """,(
            titulo,
            disciplina,
            data,
            prioridade,
            status,
            descricao,
            id_tarefa
        ))

        self.conexao.commit()

        self.adicionar_item(
            linha,
            0,
            titulo
        )

        self.adicionar_item(
            linha,
            1,
            disciplina
        )

        self.adicionar_item(
            linha,
            2,
            data
        )

        self.adicionar_item(
            linha,
            3,
            prioridade
        )

        self.adicionar_item(
            linha,
            4,
            status
        )

        self.tabela.item(
            linha,
            0
        ).setData(
            Qt.UserRole,
            {
                "id": id_tarefa,
                "descricao": descricao
            }
        )

        janela.close()

    def concluir_tarefa(self):

        linha = self.tabela.currentRow()

        if linha < 0:
            return

        dados = self.tabela.item(
            linha,
            0
        ).data(
            Qt.UserRole
        )

        self.cursor.execute(
            """
            UPDATE tarefas
            SET status=?
            WHERE id=?
            """,
            (
                "Concluído",
                dados["id"]
            )
        )

        self.conexao.commit()

        self.adicionar_item(
            linha,
            4,
            "Concluído"
        )

        self.tabela.item(
            linha,
            0
        ).setData(
            Qt.UserRole,
            {
                "id": dados["id"],
                "descricao": dados["descricao"]
            }
        )

        self.atualizar_estatisticas()

    def atualizar_estatisticas(self):

        total = self.tabela.rowCount()

        concluidas = 0

        for linha in range(total):

            item = self.tabela.item(
                linha,
                4
            )

            if item:

                if item.text() == "Concluído":

                    concluidas += 1

        pendentes = total - concluidas

        self.lblTotal.setText(
            f"Total: {total}"
        )

        self.lblPendentes.setText(
            f"Pendentes: {pendentes}"
        )

        self.lblConcluidas.setText(
            f"Concluídas: {concluidas}"
        )


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    window = Main()

    window.show()

    sys.exit(
        app.exec_()
    )