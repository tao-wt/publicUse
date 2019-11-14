#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/wait.h>


#define	BUFFSIZE	4096

int
main(void)
{
	int		n, m, fd;
	char	buf[BUFFSIZE];
    if ((fd = open("/home/tao/file.test", O_RDONLY)) > 0) {
        m = 0;
	    while ((n = read(fd, buf, BUFFSIZE)) > 0) {
            printf(":%d", m++);
		    if (write(STDOUT_FILENO, buf, n) != n) {
                printf("write error");
            }
        }
	    if (n < 0) {
		    printf("read error");
            exit(1);
        }
    } else {
        printf("open error");
    }
	exit(0);
}
