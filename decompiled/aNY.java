/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.Optional;

public class aNY
implements aqz {
    protected int o;
    protected int elr;
    protected aOc[] eql;
    protected aNZ[] eqm;
    protected Optional<Integer> eqn;
    protected int eks;

    public int d() {
        return this.o;
    }

    public int blh() {
        return this.elr;
    }

    public aOc[] ctO() {
        return this.eql;
    }

    public aNZ[] ctP() {
        return this.eqm;
    }

    public Optional<Integer> ctQ() {
        return this.eqn;
    }

    public int cnG() {
        return this.eks;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.elr = 0;
        this.eql = null;
        this.eqm = null;
        int n = 0;
        this.eqn = Optional.ofNullable(n);
        this.eks = 0;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.elr = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.eql = new aOc[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.eql[n2] = new aOc();
            ((aOC)this.eql[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.eqm = new aNZ[n2];
        for (n = 0; n < n2; ++n) {
            this.eqm[n] = new aNZ();
            ((aNz)this.eqm[n]).a(aqH2);
        }
        if (aqH2.bxv()) {
            n = aqH2.bGI();
            this.eqn = Optional.of(n);
        } else {
            this.eqn = Optional.empty();
        }
        this.eks = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oBl.d();
    }
}
