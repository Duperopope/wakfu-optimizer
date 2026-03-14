/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  apT
 *  apU
 *  apV
 *  apX
 *  aql
 *  org.apache.commons.pool.ObjectPool
 *  org.apache.commons.pool.PoolableObjectFactory
 *  org.apache.commons.pool.impl.StackObjectPool
 *  org.slf4j.Logger
 *  org.slf4j.LoggerFactory
 */
import java.util.ArrayList;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import org.apache.commons.pool.ObjectPool;
import org.apache.commons.pool.PoolableObjectFactory;
import org.apache.commons.pool.impl.StackObjectPool;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class apS
extends Thread {
    private static final boolean cPd = false;
    protected static final Logger cPe = LoggerFactory.getLogger(apY.class);
    protected final ArrayList<aql> cPf = new ArrayList();
    private final Queue<apU> cPg = new ConcurrentLinkedQueue<apU>();
    private volatile boolean btq;
    private int cPh;
    private final Lock cPi = new ReentrantLock();
    private final Condition cPj = this.cPi.newCondition();
    protected static final String cPk = "id";
    protected static final int cPl = "id".hashCode();
    private final ObjectPool cPm = new StackObjectPool((PoolableObjectFactory)new apT(this));

    private apU bFX() {
        try {
            return (apU)this.cPm.borrowObject();
        }
        catch (Exception exception) {
            cPe.error("Exception lev\u00e9e lors d'un checkOut d'op\u00e9ration", (Throwable)exception);
            return null;
        }
    }

    private void a(apU apU2) {
        try {
            this.cPm.returnObject((Object)apU2);
        }
        catch (Exception exception) {
            cPe.error("Exception lev\u00e9e lors du retour au pool d'un process", (Throwable)exception);
        }
    }

    public void a(aql aql2) {
        if (!this.cPf.contains(aql2)) {
            this.cPf.add(aql2);
        }
    }

    public void b(aql aql2) {
        this.cPf.remove(aql2);
    }

    @Override
    public synchronized void start() {
        if (!this.btq) {
            this.btq = true;
            super.start();
        }
    }

    public void aKM() {
        this.a(apV.cPr, null);
    }

    public boolean bhl() {
        return this.btq;
    }

    public void cL(boolean bl) {
        this.btq = bl;
        this.bFY();
    }

    private void bFY() {
        this.cPi.lock();
        this.cPj.signal();
        this.cPi.unlock();
    }

    public void a(apV apV2, Object object) {
        apU apU2 = this.bFX();
        if (apU2 != null) {
            apU2.cPn = apV2;
            apU2.cPo = object;
            this.cPg.offer(apU2);
            this.bFY();
        }
    }

    public int bFZ() {
        return this.cPg.size();
    }

    public int bGa() {
        return this.cPh;
    }

    public void ty(int n) {
        this.cPh = n;
    }

    public abstract apX a(int var1, apX var2);

    public abstract apX[] a(apX var1);

    public abstract apX[] a(String var1, Object var2, apX var3);

    protected abstract boolean bGb();

    protected abstract void b(apX var1);

    protected abstract void c(apX var1);

    protected abstract String bGc();

    protected abstract void bGd();

    /*
     * WARNING - Removed try catching itself - possible behaviour change.
     */
    @Override
    public void run() {
        cPe.info("BinaryStorage started " + String.valueOf(this));
        int n = 0;
        int n2 = 0;
        int n3 = 0;
        this.btq = true;
        while (this.btq) {
            apU apU2;
            while ((apU2 = this.cPg.poll()) != null) {
                apV apV2 = apU2.cPn;
                switch (apV2.ordinal()) {
                    case 0: {
                        ++n3;
                        Object object = (apX)apU2.cPo;
                        this.b((apX)object);
                        for (aql aql2 : this.cPf) {
                            aql2.b(this, (apX)object);
                        }
                        break;
                    }
                    case 1: {
                        ++n2;
                        Object object = (apX)apU2.cPo;
                        this.c((apX)object);
                        for (aql aql2 : this.cPf) {
                            aql2.a(this, (apX)object);
                        }
                        break;
                    }
                    case 2: {
                        this.cL(false);
                        for (aql aql3 : this.cPf) {
                            aql3.c(this);
                        }
                        break;
                    }
                }
                ++n;
                this.a(apU2);
            }
            if (!this.btq || !this.cPi.tryLock()) continue;
            try {
                this.cPj.await();
            }
            catch (InterruptedException interruptedException) {
                cPe.warn("Interrupt", (Throwable)interruptedException);
            }
            finally {
                this.cPi.unlock();
            }
        }
        cPe.info("BinaryStorage stopped : " + n + " operations, " + n2 + " saved, " + n3 + " destroyed");
    }
}
