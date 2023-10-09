/* entry point of our kernel */
ENTRY(_start)

SECTIONS
{
	/* we need 2KiB of space at least */
	. = 2K;

  	/* text section */
	.text BLOCK(1) : ALIGN(1)
	{
		*(.multiboot)
		*(.text)
	}

	/* read only data section */
	.rodata BLOCK(1) : ALIGN(1)
	{
		*(.rodata)
	}

	/* data section */
	.data BLOCK(1) : ALIGN(1)
	{
		*(.data)
	}

	/* bss section */
	.bss BLOCK(1) : ALIGN(1)
	{
		*(COMMON)
		*(.bss)
	}

}