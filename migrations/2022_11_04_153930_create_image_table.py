from orator.migrations import Migration


class CreateImageTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('image') as table:
            table.increments('id')
            table.big_integer('milvus_id').default(0)
            table.string('image_path', 255).default('')
            table.string('md5', 32).default('').unique()
            table.integer('size').default(0)
            table.timestamps()
        pass

    def down(self):
        """
        Revert the migrations.
        """
        pass
